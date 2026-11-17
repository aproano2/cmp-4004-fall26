"""Shared results format for every arm of HW2 (A, B, B', C).

All arms write one CSV row per problem with exactly these COLUMNS, so
code/evaluation.py can concatenate results/arm_*.csv without any reshaping.

Required by hw2.md ("Instrumentation"): per instance and per arm,
correct / incorrect / no-answer, wall-clock, tokens, and solver time
separately from LLM time.

    from results_schema import COLUMNS, grade, write_results

Column meanings
---------------
problem_id     F01 ... D20
difficulty     facil | intermedio | dificil
arm            A | B | B' | C
outcome        correct | incorrect | no_answer           (see grade())
answer         final answer as JSON ({"OP1": "TORNO", ...}); "" if none
solver_status  unique | multiple | unsat | timeout | spec_error | none
               (status of the LAST solver call; "none" for arm C)
attempts       model-generation attempts used (B' = 1..4: first + up to 3 refinements;
               A = 1, B = 1, C = 1)
wall_s         wall-clock seconds for the whole instance (LLM + solver + parsing)
llm_s          seconds spent waiting for the LLM (0 for arm A)
solver_s       seconds spent inside the solver (0 for arm C)
tokens_in      prompt tokens summed over all attempts (0 for arm A)
tokens_out     completion tokens summed over all attempts (0 for arm A)
cost_usd       money cost of the instance (tokens x price; 0 for arm A)
model          LLM id and size (e.g. "llama-3.1-8b-instant"); "human" for arm A
error_category taxonomy label for failures (filled during error analysis); "" if correct
error_message  last solver / parser error text, truncated; "" if none
timestamp      ISO-8601 time the row was produced
"""
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

COLUMNS = [
    "problem_id", "difficulty", "arm", "outcome", "answer", "solver_status", "attempts",
    "wall_s", "llm_s", "solver_s", "tokens_in", "tokens_out", "cost_usd", "model",
    "error_category", "error_message", "timestamp",
]
OUTCOMES = ("correct", "incorrect", "no_answer")


def grade(answer: dict | None, solution: dict) -> str:
    """Grading rule shared by all arms.

    - no_answer: the arm produced nothing usable (None, not a dict, empty).
    - correct:   every ground-truth variable has exactly the ground-truth value.
                 Values are compared as strings, case-insensitive and trimmed, so
                 3 == "3" and "Torno" == "TORNO". Extra keys are ignored.
    - incorrect: anything else (missing keys count as wrong).

    Policy for solver_status == "multiple" (arms B/B'): the arm returns the first
    solution the solver found and it is graded like any answer. That is the
    taxonomy row "under-constrained, wrong one returned".
    unsat / timeout / spec_error -> the arm has no answer -> no_answer.
    """
    if not isinstance(answer, dict) or not answer:
        return "no_answer"

    def norm(v):
        return str(v).strip().upper()

    for var, val in solution.items():
        if var not in answer or norm(answer[var]) != norm(val):
            return "incorrect"
    return "correct"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def make_row(**kw) -> dict:
    """Fill defaults, serialize the answer, validate the outcome."""
    row = {c: "" for c in COLUMNS}
    row.update({"attempts": 1, "llm_s": 0.0, "solver_s": 0.0, "tokens_in": 0, "tokens_out": 0,
                "cost_usd": 0.0, "solver_status": "none", "timestamp": now_iso()})
    unknown = set(kw) - set(COLUMNS)
    if unknown:
        raise KeyError(f"unknown result columns: {sorted(unknown)}")
    row.update(kw)
    if row["outcome"] not in OUTCOMES:
        raise ValueError(f"outcome must be one of {OUTCOMES}, got {row['outcome']!r}")
    if isinstance(row["answer"], dict):
        row["answer"] = json.dumps(row["answer"], ensure_ascii=False, sort_keys=True)
    elif row["answer"] is None:
        row["answer"] = ""
    for k in ("wall_s", "llm_s", "solver_s"):
        row[k] = f"{float(row[k]):.6f}"
    row["cost_usd"] = f"{float(row['cost_usd']):.6f}"
    row["error_message"] = str(row["error_message"])[:300].replace("\n", " ")
    return row


def write_results(rows: list[dict], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)
