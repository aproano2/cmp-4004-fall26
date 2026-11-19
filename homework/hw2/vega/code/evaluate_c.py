"""Grade arm C raw records separately from generation; never sends data to an LLM.

    python code/evaluate_c.py results/arm_c_raw.jsonl [--input-price P --output-price Q]
"""
import argparse
import json
from pathlib import Path

from results_schema import grade, make_row, write_results

ROOT = Path(__file__).resolve().parent.parent


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("raw", type=Path, help="ungraded JSONL from arm_c.py")
    p.add_argument("--out", type=Path, default=ROOT / "results/arm_c.csv")
    p.add_argument("--input-price", type=float, help="USD per million input tokens")
    p.add_argument("--output-price", type=float, help="USD per million output tokens")
    args = p.parse_args()
    if (args.input_price is None) != (args.output_price is None):
        p.error("supply both token prices or neither")
    if args.out.exists():
        raise FileExistsError(f"refusing to overwrite {args.out}")
    gt = json.loads((ROOT / "problems/ground_truth/ground_truth.json").read_text(encoding="utf-8"))
    solutions = {problem["id"]: problem["solution"] for problem in gt["problems"]}
    rows = []
    for line in args.raw.read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        tokens_known = r["tokens_in"] is not None and r["tokens_out"] is not None
        priced = tokens_known and args.input_price is not None
        cost = (r["tokens_in"] * args.input_price + r["tokens_out"] * args.output_price) / 1e6 if priced else 0
        row = make_row(problem_id=r["problem_id"], difficulty=r["difficulty"], arm="C",
                       outcome=grade(r["answer"], solutions[r["problem_id"]]), answer=r["answer"],
                       solver_status=r["solver_status"], attempts=1, wall_s=r["wall_s"],
                       llm_s=r["llm_s"], solver_s=0, tokens_in=r["tokens_in"],
                       tokens_out=r["tokens_out"], cost_usd=cost, model=r["model"],
                       error_message=r["error_message"])
        if not priced:
            row["cost_usd"] = ""  # Unknown is not free.
        rows.append(row)
    write_results(rows, args.out)
    print(f"C: {sum(r['outcome'] == 'correct' for r in rows)}/{len(rows)} -> {args.out}")


if __name__ == "__main__":
    main()
