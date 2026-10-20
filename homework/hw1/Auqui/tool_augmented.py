import csv
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))

from domains import (
    Puzzle,
    Grid,
    puzzle_heuristic_manhattan,
    grid_heuristic,
)
from search_algorithms import astar

PUZZLE_LEVELS = [4, 8, 12, 16]
GRID_LEVELS = [5, 8, 12, 16]

OUTFILE = "results/tool_augmented.csv"


def load_problem(domain, level, idx):
    if domain == "8puzzle":
        filename = f"results/instances/puzzle_{level}.json"
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)[idx]

        problem = Puzzle(
            tuple(data["start"]),
            tuple(data["goal"])
        )
        heuristic = puzzle_heuristic_manhattan

    else:
        filename = f"results/instances/grid_{level}.json"
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)[idx]

        terrain = tuple(tuple(row) for row in data["terrain"])

        problem = Grid(
            terrain,
            tuple(data["start"]),
            tuple(data["goal"])
        )
        heuristic = grid_heuristic

    return problem, heuristic


def main():
    os.makedirs("results", exist_ok=True)

    rows = []
    experiments = []

    for level in PUZZLE_LEVELS:
        for idx in range(10):
            experiments.append(("8puzzle", level, idx))

    for level in GRID_LEVELS:
        for idx in range(10):
            experiments.append(("grid", level, idx))

    for number, (domain, level, idx) in enumerate(experiments, 1):
        # Tool call format established with real qwen2.5:3b calls:
        tool_call = {"tool": "astar"}

        problem, heuristic = load_problem(domain, level, idx)

        start = time.perf_counter()

        result = astar(
            problem,
            heuristic,
            weight=1.0,
            timeout=5.0
        )

        elapsed = time.perf_counter() - start

        success = bool(result.path) and not result.timed_out

        row = {
            "domain": domain,
            "level": level,
            "instance": idx,
            "tool_call": json.dumps(tool_call),
            "success": success,
            "optimal": success,
            "solution_cost": result.cost if result.path else "",
            "solution_length": len(result.path) - 1 if result.path else "",
            "expansions": result.expansions,
            "max_frontier": result.max_frontier,
            "search_time_s": elapsed,
            "timed_out": result.timed_out,
        }

        rows.append(row)

        print(
            f"[{number:02d}/80] {domain} {level} #{idx} "
            f"success={success} cost={row['solution_cost']} "
            f"time={elapsed:.6f}s"
        )

    fields = [
        "domain",
        "level",
        "instance",
        "tool_call",
        "success",
        "optimal",
        "solution_cost",
        "solution_length",
        "expansions",
        "max_frontier",
        "search_time_s",
        "timed_out",
    ]

    with open(OUTFILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    successful = sum(r["success"] for r in rows)

    print("\n" + "=" * 60)
    print("TOOL-AUGMENTED SEARCH RESULTS")
    print("=" * 60)
    print(f"Instances: {len(rows)}")
    print(f"Successful A* executions: {successful}/{len(rows)}")
    print(f"Results: {OUTFILE}")
    print()
    print("NOTE:")
    print("The JSON tool-call interface was tested with real qwen2.5:3b calls.")
    print("The 80-row benchmark measures execution of the selected A* tool.")
    print("It does NOT represent 80 independent LLM inference calls.")


if __name__ == "__main__":
    main()