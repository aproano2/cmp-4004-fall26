"""run_tool_arm.py -- tool-augmented arm of the duel (the model may call OUR A*).

Flow per instance:
  1. the model gets the task + a tool `astar_solve(grid)`; it must COPY the grid into
     a JSON tool call (this is the "natural language -> formal model" step);
  2. WE run A* (engine.py) on the grid the model sent and return {"path","cost"};
  3. the model writes the final two lines; OUR validator judges them against the
     ORIGINAL grid (a mis-copied grid therefore shows up as a failure, and we log it).
Extra diagnostics: tool_called, grid_copy_exact, final_matches_tool.

  python3 run_tool_arm.py --sizes 5 --limit 2 --verbose    # pilot
  python3 run_tool_arm.py                                   # full: 4 sizes x 10
Resumable through ../.llm_cache.  Writes ../results/tool_grid.csv.
"""
import argparse
import csv
import json
import re
import time
import urllib.error
from pathlib import Path

import duel_lib as D
import engine
import gridworld as GW
import heuristics_grid as HG
import llm_client as L

HERE = Path(__file__).parent
OUT = HERE.parent / "results" / "tool_grid.csv"
ALLOWED = set(".,~SG")
CAP_CALL1, CAP_CALL2 = 700, 120      # token caps: 1st call must re-type the grid

TOOLS = [{"type": "function", "function": {
    "name": "astar_solve",
    "description": "Exact A* solver for a weighted grid. Returns the minimum-cost "
                   "path as U/D/L/R letters and its total cost.",
    "parameters": {"type": "object", "properties": {
        "grid": {"type": "array", "items": {"type": "string"},
                 "description": "The grid, one string per row, using only the "
                                "characters . , ~ S G exactly as in the problem."}},
        "required": ["grid"]}}}]

FIELDS = ["size", "instance", "category", "reason", "reported_cost", "true_cost",
          "optimal_cost", "cost_reported_ok", "path", "tool_called", "grid_copy_exact",
          "tool_error", "tool_path", "final_matches_tool", "n_calls", "prompt_tokens",
          "output_tokens", "gen_latency_s", "key"]


def prompt_for_tool(grid):
    """Same task text and same information as the direct arm; only the grid is shown
    compactly (no spaces between cells) because that is the tool's input format."""
    head = D.prompt_for(grid, "direct").split("Grid:\n")[0]
    return head + (
        "Grid (one row per line):\n" + "\n".join(grid) + "\n\n"
        "You have a tool called astar_solve that returns the exact minimum-cost path "
        "for a grid. Call it with the grid exactly as shown above: a list with one "
        "string per row. After you receive the result, reply with exactly two lines "
        "and nothing else:\n"
        "PATH: <letters U/D/L/R, no separators>\n"
        "COST: <integer>\n")


def normalize_grid(arg):
    """Formatting only (spaces / newlines); the CONTENT is never altered."""
    if isinstance(arg, str):
        arg = arg.splitlines()
    if not (isinstance(arg, list) and all(isinstance(r, str) for r in arg)):
        return None
    return ["".join(r.split()) for r in arg if r.strip()]


def tool_astar(arg):
    """Run OUR A* on the grid the model sent. Returns a JSON-able dict."""
    rows = normalize_grid(arg)
    if not rows:
        return {"error": "grid must be a list of strings"}
    if len({len(r) for r in rows}) != 1:
        return {"error": "rows must all have the same length"}
    flat = "".join(rows)
    if set(flat) - ALLOWED:
        return {"error": "unknown characters; use only . , ~ S G"}
    if flat.count("S") != 1 or flat.count("G") != 1:
        return {"error": "grid needs exactly one S and one G"}
    res = engine.run(GW.GridProblem(rows), "astar", HG.h_manhattan_scaled, timeout=30)
    if res["status"] != "ok":
        return {"error": res["status"]}
    return {"path": "".join(res["path"]), "cost": res["cost"]}


def extract_call(rec):
    """Return the grid argument of the first tool call, or (None) if there is none."""
    calls = rec.get("tool_calls") or []
    if calls:
        args = calls[0].get("function", {}).get("arguments", {})
        if isinstance(args, str):
            try:
                args = json.loads(args)
            except ValueError:
                return None, calls
        return args.get("grid"), calls
    m = re.search(r'"grid"\s*:\s*(\[.*?\])', rec["text"], flags=re.S)   # JSON typed as text
    if m:
        try:
            return json.loads(m.group(1)), None
        except ValueError:
            pass
    return None, None


def run_instance(grid, size, i):
    prompt = prompt_for_tool(grid)
    msgs = [{"role": "user", "content": prompt}]
    r1 = L.chat(msgs, num_predict=CAP_CALL1, tools=TOOLS, tag=f"tool_grid{size}_{i}_c1")
    recs = [r1]
    grid_arg, calls = extract_call(r1)
    info = {"tool_called": grid_arg is not None, "grid_copy_exact": None,
            "tool_error": None, "tool_path": None}
    if grid_arg is None:                         # the model answered without the tool
        final_text = r1["text"]
    else:
        sent = normalize_grid(grid_arg)
        info["grid_copy_exact"] = sent == ["".join(r.split()) for r in grid]
        result = tool_astar(grid_arg)
        info["tool_error"] = result.get("error")
        info["tool_path"] = result.get("path")
        asst = {"role": "assistant", "content": r1["text"]}
        if calls:
            asst["tool_calls"] = calls
        msgs2 = msgs + [asst, {"role": "tool", "tool_name": "astar_solve",
                               "content": json.dumps(result)}]
        r2 = L.chat(msgs2, num_predict=CAP_CALL2, tools=TOOLS,
                    tag=f"tool_grid{size}_{i}_c2")
        recs.append(r2)
        final_text = r2["text"]
    v = D.validate(grid, final_text)
    info["final_matches_tool"] = (None if info["tool_path"] is None
                                  else v["path"] == info["tool_path"])
    return v, info, recs


def main(sizes, limit, verbose):
    bank = GW.load_instances(HERE / "instances_grid.json")
    OUT.parent.mkdir(exist_ok=True)
    L.MAX_RETRIES = 1                 # a malformed tool call fails deterministically
    rows, t_start = [], time.perf_counter()
    for size in sizes:
        for i, grid in enumerate(bank[size][:limit]):
            try:
                v, info, recs = run_instance(grid, size, i)
            except urllib.error.HTTPError as e:   # server refused the model's tool call
                v = {"category": "tool_call_failed", "reason": f"HTTP {e.code}",
                     "reported_cost": None, "true_cost": None, "optimal_cost": None,
                     "cost_reported_ok": None, "path": None}
                info = {"tool_called": None, "grid_copy_exact": None,
                        "tool_error": f"HTTP {e.code} from server", "tool_path": None,
                        "final_matches_tool": None}
                recs = []
            rows.append({"size": size, "instance": i, "category": v["category"],
                         "reason": v["reason"], "reported_cost": v["reported_cost"],
                         "true_cost": v["true_cost"], "optimal_cost": v["optimal_cost"],
                         "cost_reported_ok": v["cost_reported_ok"], "path": v["path"],
                         **info, "n_calls": len(recs),
                         "prompt_tokens": sum(r["prompt_tokens"] or 0 for r in recs),
                         "output_tokens": sum(r["output_tokens"] or 0 for r in recs),
                         "gen_latency_s": round(sum(r["gen_latency_s"] for r in recs), 2),
                         "key": recs[0]["key"] if recs else ""})
            with open(OUT, "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=FIELDS)
                w.writeheader()
                w.writerows(rows)
            print(f"[{size}x{size} #{i}] {v['category']:<10} tool_called={info['tool_called']} "
                  f"copy_exact={info['grid_copy_exact']} tool_err={info['tool_error']} "
                  f"calls={len(recs)} {rows[-1]['gen_latency_s']}s", flush=True)
            if verbose:
                for k, r in enumerate(recs, 1):
                    print(f"   --- call {k}: text={r['text'][:200]!r} "
                          f"tool_calls={json.dumps(r.get('tool_calls'))[:300]}")
                print(f"   --- optimal cost = {D.optimal_cost(grid)}", flush=True)
    counts = {}
    for r in rows:
        counts[r["category"]] = counts.get(r["category"], 0) + 1
    print(f"\n{len(rows)} instances in {time.perf_counter() - t_start:.0f}s -> {counts}")
    print("wrote", OUT)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sizes", type=int, nargs="+", default=[5, 8, 12, 16])
    ap.add_argument("--limit", type=int, default=10)
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()
    main(a.sizes, a.limit, a.verbose)
