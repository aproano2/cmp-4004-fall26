import csv
import json
import sys
from pathlib import Path
from time import perf_counter

submission = Path(__file__).resolve().parents[1]
repo = submission.parents[2]
sys.path.insert(0, str(repo / "studios" / "week-07"))
from dpll import dpll

fields = [
    "problem_id", "difficulty", "arm", "expected_status",
    "predicted_status", "outcome", "wall_ms", "solver_ms",
    "llm_ms", "input_tokens", "output_tokens",
]


def run_problem(path):
    start = perf_counter()
    problem = json.loads(path.read_text(encoding="utf-8"))
    clauses = [frozenset(clause) for clause in problem["clauses"]]

    solver_start = perf_counter()
    model = dpll(clauses)
    solver_ms = (perf_counter() - solver_start) * 1000

    actual = "SAT" if model is not None else "UNSAT"
    wall_ms = (perf_counter() - start) * 1000
    truth = problem["ground_truth"]

    if truth["status"] == "SAT":
        witness = {
            number: truth["witness"][name]
            for name, number in problem["variables"].items()
        }
        if not all(
            any(witness[abs(lit)] == (lit > 0) for lit in clause)
            for clause in clauses
        ):
            raise SystemExit(f"{problem['id']}: la solución manual incumple una regla.")

    return {
        "problem_id": problem["id"],
        "difficulty": problem["difficulty"],
        "arm": "A",
        "expected_status": truth["status"],
        "predicted_status": actual,
        "outcome": "correct" if actual == truth["status"] else "incorrect",
        "wall_ms": f"{wall_ms:.6f}",
        "solver_ms": f"{solver_ms:.6f}",
        "llm_ms": "",
        "input_tokens": "",
        "output_tokens": "",
    }


def main():
    paths = sorted((submission / "problems").glob("sat_*.json"))
    if len(paths) != 20:
        raise SystemExit(f"Se esperaban 20 archivos y se encontraron {len(paths)}.")

    rows = [run_problem(path) for path in paths]
    output = submission / "results" / "arm_a.csv"
    with output.open("x", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    correct = sum(row["outcome"] == "correct" for row in rows)
    print(f"Brazo A: {correct}/{len(rows)} respuestas correctas.")
    print(f"CSV guardado en {output.relative_to(repo)}")
    for row in rows:
        if row["outcome"] == "incorrect":
            print(
                f"{row['problem_id']}: esperado {row['expected_status']}, "
                f"DPLL devolvió {row['predicted_status']}"
            )


if __name__ == "__main__":
    main()
