"""Run arms A, B, B', C over the dataset (optionally several runs/seeds) and write results incrementally.

Outputs (in --outdir, default results/):
  metrics.csv          one row per (problem, run, arm)
  records.jsonl        the same rows + every attempt of every arm with the verbatim model output
  taxonomy.json        every arm-B failure, classified
  bprime_traces.json   per-attempt classification of every B' run (for the refinement analysis)
"""
import argparse, csv, json, sys
from pathlib import Path

import llm
from arms import run_hand, run_hybrid, run_direct
from encoding import reference_clause_count
from taxonomy import classify_attempt, semantic_class
from prompts import extract_json

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ["problem_id", "difficulty", "vertices", "edges", "reference_clauses", "run", "seed", "temperature", "model",
          "arm", "outcome", "correct", "status", "announced_failure", "attempts", "trajectory", "semantic_class",
          "violated_edges", "wall_time_s", "llm_time_s", "solver_time_s", "prompt_tokens", "completion_tokens",
          "tokens", "all_cached", "answer_json", "error"]


def semantic_of_final(problem, rec):
    """Semantic class of the last parsed CNF (also for *correct* answers: 'right for the wrong reasons')."""
    last = rec["trace"][-1]
    try:
        return semantic_class(problem, extract_json(last["raw_output"])["clauses"]) if last["status"] in ("SAT", "UNSAT", "DECODE_ERROR") else ""
    except Exception:
        return ""


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=3, help="independent repetitions (seeds 0..runs-1)")
    ap.add_argument("--temperature", type=float, default=0.7, help="use 0 with --runs 1 for a greedy run")
    ap.add_argument("--max-attempts", type=int, default=3)
    ap.add_argument("--feedback", choices=["basic", "rich"], default="basic",
                    help="basic = solver status only (default); rich = adds an UNSAT core (ablation)")
    ap.add_argument("--problems", default=str(ROOT / "problems" / "dataset.json"))
    ap.add_argument("--outdir", default=str(ROOT / "results"))
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args(argv)

    data = json.loads(Path(args.problems).read_text(encoding="utf-8"))
    if args.limit:
        data = data[:args.limit]
    if args.temperature == 0 and args.runs > 1:
        print("AVISO: con temperature=0 todas las corridas serán idénticas; usa --runs 1 o --temperature > 0.")
    out = Path(args.outdir); out.mkdir(parents=True, exist_ok=True)
    taxonomy, bprime_traces = [], []
    total = len(data) * args.runs
    done = 0
    with (out / "metrics.csv").open("w", newline="", encoding="utf-8") as fcsv, \
         (out / "records.jsonl").open("w", encoding="utf-8") as fjson:
        writer = csv.DictWriter(fcsv, fieldnames=FIELDS); writer.writeheader()
        for run in range(args.runs):
            for problem in data:
                done += 1
                print(f"[{done}/{total}] run={run} {problem['id']} ({problem['difficulty']})", flush=True)
                kw = dict(temperature=args.temperature, seed=run)
                recs = [run_hand(problem),
                        run_hybrid(problem, False, 1, feedback_level=args.feedback, **kw),
                        run_hybrid(problem, True, args.max_attempts, feedback_level=args.feedback, **kw),
                        run_direct(problem, **kw)]
                for rec in recs:
                    if rec["arm"] in ("B", "B_prime"):
                        rec["semantic_class"] = semantic_of_final(problem, rec)
                    row = {"problem_id": problem["id"], "difficulty": problem["difficulty"],
                           "vertices": len(problem["vertices"]), "edges": len(problem["edges"]),
                           "reference_clauses": reference_clause_count(problem), "run": run, "seed": run,
                           "temperature": args.temperature, "model": llm.MODEL,
                           "answer_json": json.dumps(rec["answer"], ensure_ascii=False),
                           **{k: rec.get(k, "") for k in FIELDS if k in rec}}
                    writer.writerow({k: row.get(k, "") for k in FIELDS})
                    fjson.write(json.dumps({**{k: row[k] for k in ("problem_id", "run", "seed")}, **rec},
                                           ensure_ascii=False) + "\n")
                b, bp = recs[1], recs[2]
                if not b["correct"]:
                    taxonomy.append({"problem_id": problem["id"], "difficulty": problem["difficulty"], "run": run,
                                     "solver_status": b["status"], "model_output": b["raw_output"],
                                     **classify_attempt(problem, b["trace"][-1])})
                bprime_traces.append({"problem_id": problem["id"], "difficulty": problem["difficulty"], "run": run,
                                      "correct": bp["correct"], "attempts": bp["attempts"],
                                      "attempt_classes": [{"attempt": t["attempt"], "status": t["status"],
                                                           **{k: v for k, v in classify_attempt(problem, t).items()
                                                              if k in ("category", "detectable_without_ground_truth", "subcause")}}
                                                          for t in bp["trace"]]})
                fcsv.flush(); fjson.flush()
    (out / "taxonomy.json").write_text(json.dumps(taxonomy, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "bprime_traces.json").write_text(json.dumps(bprime_traces, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Listo: {done} (problema,corrida) -> {done*4} filas; {len(taxonomy)} fallos de B clasificados.")


if __name__ == "__main__":
    main()
