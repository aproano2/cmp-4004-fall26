"""Corre los cuatro brazos sobre los 40 problemas y guarda la evidencia cruda.

    python code/run_all.py                       # Ollama, qwen2.5:3b
    python code/run_all.py --stochastic-reps 0   # solo la corrida a temperatura 0

Corridas:
  rep 0          temperatura 0, semilla 0   -> la corrida principal (scorecard,
                                               taxonomía detallada)
  rep 1..4       temperatura 0.7, semillas 1..4 -> varianza entre corridas;
                                               con la rep 0 son 5 corridas por
                                               instancia (reproducibilidad: 'run 5×')
Cada llamada queda en .llm_cache/: si se corta, el mismo comando sigue donde quedó.

Salidas (results/):
  runs.csv                   una fila por (brazo, problema, rep)
  refinement_attempts.csv    cada intento del bucle B′
  arm_b_attempts.jsonl       texto completo de cada intento de B/B′ (para taxonomy.md)
  arm_c_outputs.jsonl        texto completo de cada respuesta de C
"""
import argparse
import csv
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from arms import run_arm_a, run_arm_b, run_arm_c   # noqa: E402
from llm import LLM                                   # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "results"


def load_problems():
    return json.loads((ROOT / "problems" / "problems.json").read_text(encoding="utf-8"))["problems"]


def write_csv(path, rows):
    if not rows:
        return
    keys = list(rows[0])
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", default="ollama")
    ap.add_argument("--model", default="qwen2.5:3b")
    ap.add_argument("--stochastic-reps", type=int, default=4)
    ap.add_argument("--temperature", type=float, default=0.7)
    ap.add_argument("--only", default="", help="ids separados por coma (pruebas)")
    args = ap.parse_args(argv)

    RES.mkdir(exist_ok=True)
    problems = load_problems()
    if args.only:
        problems = [p for p in problems if p["id"] in args.only.split(",")]
    model = LLM(args.backend, args.model)
    runs = [(0, 0.0, 0)] + [(r, args.temperature, r) for r in range(1, args.stochastic_reps + 1)]

    rows, attempts_rows = [], []
    fb = open(RES / "arm_b_attempts.jsonl", "w", encoding="utf-8")
    fc = open(RES / "arm_c_outputs.jsonl", "w", encoding="utf-8")

    for p in problems:
        rows.append(run_arm_a(p))
    t_start = time.perf_counter()
    total = len(runs) * len(problems)
    done = 0
    for rep, temp, seed in runs:
        for p in problems:
            rb, rp, attempts = run_arm_b(model, p, temperature=temp, seed=seed, rep=rep)
            rc, ctext = run_arm_c(model, p, temperature=temp, seed=seed, rep=rep)
            rows += [rb, rp, rc]
            for a in attempts:
                attempts_rows.append({"problem": p["id"], "level": p["level"], "rep": rep,
                                      "temperature": temp, "iteration": a["iteration"],
                                      "stage": a["stage"], "error": a["error"],
                                      "n_solutions": a["n_solutions"], "correct": a["correct"]})
                fb.write(json.dumps({"problem": p["id"], "rep": rep, "temperature": temp,
                                     "iteration": a["iteration"], "stage": a["stage"],
                                     "error": a["error"], "n_solutions": a["n_solutions"],
                                     "correct": a["correct"], "solution": a["solution"],
                                     "spec": a["spec"], "text": a["text"]},
                                    ensure_ascii=False) + "\n")
            fc.write(json.dumps({"problem": p["id"], "rep": rep, "temperature": temp,
                                 "outcome": rc["outcome"], "text": ctext},
                                ensure_ascii=False) + "\n")
            done += 1
            el = time.perf_counter() - t_start
            print(f"[{done}/{total}] rep {rep} T={temp} {p['id']}: "
                  f"B={rb['outcome']}/{rb['stage']}  B'={rp['outcome']} "
                  f"({rp['iterations']} rondas)  C={rc['outcome']}   "
                  f"{el / 60:.1f} min", flush=True)
    fb.close()
    fc.close()
    write_csv(RES / "runs.csv", rows)
    write_csv(RES / "refinement_attempts.csv", attempts_rows)
    if args.backend == "ollama" and not args.only:
        print(f"caché: {model.prune()} transcripts viejos borrados")
    print("Listo. Ahora:  python code/analyze.py")


if __name__ == "__main__":
    main()
