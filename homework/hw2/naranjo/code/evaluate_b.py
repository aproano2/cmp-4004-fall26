"""Grade B/B' raw records separately from generation; never sends data to an LLM."""
import argparse
import json
from pathlib import Path

from results_schema import grade, make_row, write_results

ROOT = Path(__file__).resolve().parent.parent


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("raw", type=Path, help="ungraded JSONL from arm_b.py")
    p.add_argument("--out-dir", type=Path, default=ROOT / "results")
    p.add_argument("--input-price", type=float, help="USD per million input tokens")
    p.add_argument("--output-price", type=float, help="USD per million output tokens")
    args = p.parse_args()
    if (args.input_price is None) != (args.output_price is None):
        p.error("supply both token prices or neither")
    gt = json.loads((ROOT / "problems/ground_truth/ground_truth.json").read_text(encoding="utf-8"))
    solutions = {problem["id"]: problem["solution"] for problem in gt["problems"]}
    rows = {"B": [], "B'": []}
    for line in args.raw.read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        tokens_known = r["tokens_in"] is not None and r["tokens_out"] is not None
        cost = ((r["tokens_in"] * args.input_price + r["tokens_out"] * args.output_price) / 1e6
                if tokens_known and args.input_price is not None else 0)
        row = make_row(problem_id=r["problem_id"], difficulty=r["difficulty"], arm=r["arm"],
                       outcome=grade(r["answer"], solutions[r["problem_id"]]), answer=r["answer"],
                       solver_status=r["solver_status"], attempts=r["attempts"], wall_s=r["wall_s"],
                       llm_s=r["llm_s"], solver_s=r["solver_s"], tokens_in=r["tokens_in"],
                       tokens_out=r["tokens_out"], cost_usd=cost, model=r["model"],
                       error_message=r["error_message"])
        if not tokens_known or args.input_price is None:
            row["cost_usd"] = ""  # Unknown is not free.
        rows[r["arm"]].append(row)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    for arm, filename in (("B", "arm_b.csv"), ("B'", "arm_b_refined.csv")):
        path = args.out_dir / filename
        if path.exists():
            raise FileExistsError(f"refusing to overwrite {path}")
        write_results(rows[arm], path)
        print(f"{arm}: {sum(r['outcome'] == 'correct' for r in rows[arm])}/{len(rows[arm])} -> {path}")


if __name__ == "__main__":
    main()
