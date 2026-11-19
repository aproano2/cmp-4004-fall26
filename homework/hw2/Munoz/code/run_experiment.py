import argparse
import csv
import json
from pathlib import Path

from run_arms import BASE, Ollama, run_arm


FIELDS = [
    "repeat", "problem_id", "difficulty", "arm", "model", "temperature", "seed",
    "status", "answer_status", "assignment", "total_time_s", "llm_time_s",
    "solver_time_s", "input_tokens", "output_tokens", "refinements",
    "success_iteration", "iteration", "error", "raw_output", "cache_file",
    "ground_truth_reviewed",
]


def write_row(writer, row, repeat):
    record = dict(row, repeat=repeat, temperature=0, seed=42)
    record["assignment"] = json.dumps(row["assignment"]) if row["assignment"] is not None else ""
    writer.writerow(record)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="llama3.2:3b")
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output", type=Path, default=BASE / "results")
    parser.add_argument("--resume", action="store_true", help="Continuar sin repetir resultados guardados.")
    args = parser.parse_args()
    if args.repeats < 1:
        parser.error("El numero de repeticiones debe ser positivo.")
    problems = json.loads((BASE / "problems/problems.json").read_text(encoding="utf-8"))
    truths = {t["id"]: t for t in json.loads(
        (BASE / "problems/ground_truth.json").read_text(encoding="utf-8"))}
    if any(not truths[p["id"]]["human_reviewed"] for p in problems):
        parser.error("Falta la revision manual de algunos problemas.")
    args.output.mkdir(parents=True, exist_ok=True)
    paths = [args.output / "results.csv", args.output / "attempts.csv"]
    existing = {}
    if args.resume:
        if not all(path.exists() for path in paths):
            parser.error("Faltan los CSV para continuar.")
        with paths[0].open(newline="", encoding="utf-8") as file:
            for record in csv.DictReader(file):
                row = {key: value if value != "" else None for key, value in record.items()}
                for key in ("repeat", "input_tokens", "output_tokens", "refinements", "success_iteration", "iteration", "seed"):
                    if row[key] is not None:
                        row[key] = int(row[key])
                for key in ("total_time_s", "llm_time_s", "solver_time_s", "temperature"):
                    row[key] = float(row[key])
                row["assignment"] = json.loads(row["assignment"]) if row["assignment"] else None
                row["ground_truth_reviewed"] = row["ground_truth_reviewed"] == "True"
                if row["model"] not in (None, args.model):
                    parser.error("El modelo debe coincidir con los resultados existentes.")
                existing[(row["repeat"], row["problem_id"], row["arm"])] = row
    elif any(path.exists() for path in paths):
        parser.error("Ya hay resultados. Usa --output con otra carpeta para una nueva ejecucion.")
    client = Ollama(args.model)
    mode = "a" if args.resume else "x"
    with paths[0].open(mode, newline="", encoding="utf-8") as results, paths[1].open(mode, newline="", encoding="utf-8") as attempts:
        writers = [csv.DictWriter(file, fieldnames=FIELDS, extrasaction="ignore") for file in (results, attempts)]
        if not args.resume:
            for writer in writers:
                writer.writeheader()
        for repeat in range(1, args.repeats + 1):
            for problem in problems:
                if all((repeat, problem["id"], arm) in existing for arm in ("A", "B", "Bp", "C")):
                    continue
                print(f"Repeticion {repeat}/{args.repeats} | {problem['id']} | Ejecutando...", flush=True)
                initial = None
                statuses = []
                for arm in ("A", "B", "Bp", "C"):
                    saved = existing.get((repeat, problem["id"], arm))
                    if saved is not None:
                        if arm == "B":
                            initial = saved
                        statuses.append(f"{arm}: {saved['status']}")
                        continue
                    row = run_arm(arm, problem, truths[problem["id"]], client, initial=initial)
                    if arm == "B":
                        initial = row
                    write_row(writers[0], row, repeat)
                    for attempt in row.get("attempts", [dict(row, iteration=0)]):
                        write_row(writers[1], dict(attempt, arm=arm), repeat)
                    results.flush()
                    attempts.flush()
                    statuses.append(f"{arm}: {row['status']}")
                print(" | ".join(statuses), flush=True)
    print(f"Guardados {len(problems) * args.repeats * 4} resultados en {args.output}", flush=True)


if __name__ == "__main__":
    main()
