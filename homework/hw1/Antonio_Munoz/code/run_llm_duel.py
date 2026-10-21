"""run_llm_duel.py -- LLM arm of the duel on the weighted grids.

  python3 run_llm_duel.py --sizes 5 --limit 2 --verbose   # quick check
  python3 run_llm_duel.py                                  # full: 4 sizes x 10

--variant direct (default, main arm): answer only, token cap 200.
--variant free: the model may reason first, token cap 1024 (optional extra arm).

Every model call goes through llm_client (cached in ../.llm_cache), so the script is
RESUMABLE: finished calls come back instantly. Every reply is classified by OUR
validator (duel_lib.py); the model is never asked whether it is right.
Writes ../results/llm_grid.csv (direct) or llm_grid_free.csv (free).
"""
import argparse
import csv
import time
from pathlib import Path

import duel_lib as D
import gridworld as GW
import llm_client as L

HERE = Path(__file__).parent
FIELDS = ["size", "instance", "category", "reason", "reported_cost", "true_cost",
          "optimal_cost", "cost_reported_ok", "path", "prompt_tokens",
          "output_tokens", "gen_latency_s", "done_reason", "cached", "key"]
DEFAULT_CAP = {"direct": 200, "free": 1024}


def main(sizes, limit, verbose, variant="direct", num_predict=None):
    num_predict = num_predict or DEFAULT_CAP[variant]
    out = HERE.parent / "results" / ("llm_grid.csv" if variant == "direct"
                                     else "llm_grid_free.csv")
    bank = GW.load_instances(HERE / "instances_grid.json")
    out.parent.mkdir(exist_ok=True)
    rows = []
    t_start = time.perf_counter()
    for size in sizes:
        for i, grid in enumerate(bank[size][:limit]):
            rec = L.chat([{"role": "user", "content": D.prompt_for(grid, variant)}],
                         num_predict=num_predict, tag=f"{variant}_grid{size}_{i}")
            v = D.validate(grid, rec["text"])
            rows.append({"size": size, "instance": i, "category": v["category"],
                         "reason": v["reason"], "reported_cost": v["reported_cost"],
                         "true_cost": v["true_cost"], "optimal_cost": v["optimal_cost"],
                         "cost_reported_ok": v["cost_reported_ok"], "path": v["path"],
                         "prompt_tokens": rec["prompt_tokens"],
                         "output_tokens": rec["output_tokens"],
                         "gen_latency_s": rec["gen_latency_s"],
                         "done_reason": rec["done_reason"], "cached": rec["cached"],
                         "key": rec["key"]})
            with open(out, "w", newline="") as f:          # rewrite after every call
                w = csv.DictWriter(f, fieldnames=FIELDS)
                w.writeheader()
                w.writerows(rows)
            print(f"[{size}x{size} #{i}] {v['category']:<10} reason={v['reason']} "
                  f"tok_in={rec['prompt_tokens']} tok_out={rec['output_tokens']} "
                  f"stop={rec['done_reason']} {rec['gen_latency_s']}s "
                  f"cached={rec['cached']}", flush=True)
            if verbose:
                print("   --- model reply (first 600 chars) ---")
                print("   " + rec["text"][:600].replace("\n", "\n   "))
                print(f"   --- optimal cost = {D.optimal_cost(grid)}", flush=True)
    counts = {}
    for r in rows:
        counts[r["category"]] = counts.get(r["category"], 0) + 1
    print(f"\n{len(rows)} replies in {time.perf_counter() - t_start:.0f}s -> {counts}")
    print("wrote", out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sizes", type=int, nargs="+", default=[5, 8, 12, 16])
    ap.add_argument("--limit", type=int, default=10, help="instances per size")
    ap.add_argument("--variant", choices=["direct", "free"], default="direct")
    ap.add_argument("--num-predict", type=int, default=None)
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()
    main(a.sizes, a.limit, a.verbose, a.variant, a.num_predict)
