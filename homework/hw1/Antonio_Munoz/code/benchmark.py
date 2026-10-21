"""benchmark.py -- Part 1 harness. Runs every algorithm on every instance and
writes RAW rows (one per algorithm x instance) to ../results/*.csv.
No statistics here: medians/IQR are computed later, from the CSVs.

Run:  python3 benchmark.py
"""
import csv
import time
from pathlib import Path

import engine
import gridworld as GW
import heuristics_8p as H8
import heuristics_grid as HG
import search as S

TIMEOUT = 10.0                     # seconds per (algorithm, instance); state it in the report
HERE = Path(__file__).parent
RESULTS = HERE.parent / "results"
FIELDS = ["domain", "level", "instance", "algo", "status", "cost", "length",
          "expansions", "max_frontier", "time_s", "path"]

ALGOS_8P = [
    ("bfs", "bfs", None), ("dfs", "dfs", None), ("ucs", "ucs", None), ("ids", "ids", None),
    ("astar_misplaced", "astar", H8.h_misplaced),
    ("astar_manhattan", "astar", H8.h_manhattan),
    ("astar_manhattan_x3", "astar", H8.scaled(H8.h_manhattan, 3)),
]
ALGOS_GRID = [
    ("bfs", "bfs", None), ("dfs", "dfs", None), ("ucs", "ucs", None), ("ids", "ids", None),
    ("astar_manhattan", "astar", HG.h_manhattan_scaled),
    ("astar_manhattan_x3", "astar", H8.scaled(HG.h_manhattan_scaled, 3)),
]


def run_domain(name, bank, make_problem, algos, outfile):
    rows = []
    for level in sorted(bank):
        for i, inst in enumerate(bank[level]):
            problem = make_problem(inst)
            for label, algo, h in algos:
                r = engine.run(problem, algo, h, timeout=TIMEOUT)
                rows.append({
                    "domain": name, "level": level, "instance": i, "algo": label,
                    "status": r["status"], "cost": r["cost"], "length": r["length"],
                    "expansions": r["expansions"], "max_frontier": r["max_frontier"],
                    "time_s": f"{r['time_s']:.6f}",
                    "path": ",".join(map(str, r["path"])) if r["path"] is not None else "",
                })
        print(f"  {name} level {level}: done")
    RESULTS.mkdir(exist_ok=True)
    with open(RESULTS / outfile, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    to = sum(r["status"] == "timeout" for r in rows)
    print(f"  -> {outfile}: {len(rows)} rows, {to} timeouts")


if __name__ == "__main__":
    t0 = time.perf_counter()
    print(f"timeout = {TIMEOUT}s")
    run_domain("8puzzle", S.load_instances(HERE / "instances_8puzzle.json"),
               S.EightPuzzle, ALGOS_8P, "classical_8puzzle.csv")
    run_domain("grid", GW.load_instances(HERE / "instances_grid.json"),
               GW.GridProblem, ALGOS_GRID, "classical_grid.csv")
    print(f"total {time.perf_counter() - t0:.0f}s")
