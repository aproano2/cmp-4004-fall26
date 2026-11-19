"""Arm A (Manual): hand-written CSP model -> solver.

    python code/arm_a.py                 # all 20 problems -> results/arm_a.csv
    python code/arm_a.py --repeats 10    # more timing repetitions
    python code/arm_a.py F01 D15         # only some problems (prints, still writes the CSV)

For each problem it takes the hand-written model (the "model" field of
problems/ground_truth/ground_truth.json, reviewed manually and verified by
code/verify_ground_truth.py), runs the same solver the other arms use
(csp_spec.solve, MRV + forward checking), and grades the answer with the shared
rule in results_schema.grade.

What an arm does with the solver result (same policy as arms B/B'):
  unique   -> answer = that solution
  multiple -> answer = first solution found (graded normally)
  unsat / timeout / spec_error -> no answer
The solver is called with max_solutions=2, which is enough to tell unique from
multiple, as a deployed system would; it does not use the stored solution.

Timing: the solver runs are milliseconds long and noisy, so each problem is solved
--repeats times and the MEDIAN wall_s / solver_s is reported. wall_s includes
loading/validating the model, solving and grading; solver_s is only the search.
There is no LLM, so llm_s, tokens and cost_usd are 0. The human time spent writing
the models is NOT included (it is a fixed cost paid once; discuss it in the
report's "Where we may have been unfair" section).

Arm A's model and the ground truth come from the same file, so arm A scores 100 %
by construction. What makes that number meaningful is the independent manual
review recorded in ground_truth.json (review.manual_review == "OK"); this script
warns if any problem has not been reviewed.
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path

from csp_spec import SpecError, solve
from results_schema import grade, make_row, write_results

ROOT = Path(__file__).resolve().parent.parent
GT = ROOT / "problems" / "ground_truth" / "ground_truth.json"
OUT = ROOT / "results" / "arm_a.csv"


def run_once(model: dict, solution: dict):
    t0 = time.perf_counter()
    try:
        r = solve(model, max_solutions=2)
        status, solver_s = r["status"], r["seconds"]
        answer = r["solutions"][0] if status in ("unique", "multiple") else None
        error = "" if answer else f"solver returned {status}"
    except SpecError as e:
        status, solver_s, answer, error = "spec_error", 0.0, None, str(e)
    outcome = grade(answer, solution)
    wall_s = time.perf_counter() - t0
    return outcome, answer, status, wall_s, solver_s, error


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("ids", nargs="*", help="problem ids to run (default: all)")
    ap.add_argument("--repeats", type=int, default=5, help="timing repetitions per problem (median)")
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args(argv)

    problems = json.loads(GT.read_text(encoding="utf-8"))["problems"]
    if args.ids:
        problems = [p for p in problems if p["id"] in set(args.ids)]
    unreviewed = [p["id"] for p in problems if p.get("review", {}).get("manual_review") != "OK"]
    if unreviewed:
        print(f"AVISO: sin revisión manual OK: {', '.join(unreviewed)}", file=sys.stderr)

    rows = []
    for p in problems:
        runs = [run_once(p["model"], p["solution"]) for _ in range(max(1, args.repeats))]
        outcome, answer, status, _, _, error = runs[0]
        if any(r[0] != outcome or r[1] != answer for r in runs):
            raise RuntimeError(f"{p['id']}: non-deterministic result across repeats")
        rows.append(make_row(
            problem_id=p["id"], difficulty=p["difficulty"], arm="A", outcome=outcome,
            answer=answer, solver_status=status, attempts=1,
            wall_s=statistics.median(r[3] for r in runs),
            solver_s=statistics.median(r[4] for r in runs),
            model="human", error_message=error,
        ))
        r = rows[-1]
        print(f"{p['id']}  {p['difficulty']:<10}  {outcome:<9}  solver={status:<8}  "
              f"wall={float(r['wall_s']) * 1000:7.2f} ms  solver={float(r['solver_s']) * 1000:7.2f} ms")

    write_results(rows, args.out)
    n_ok = sum(r["outcome"] == "correct" for r in rows)
    print(f"\nBrazo A: {n_ok}/{len(rows)} correctas -> {args.out.relative_to(ROOT) if args.out.is_relative_to(ROOT) else args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
