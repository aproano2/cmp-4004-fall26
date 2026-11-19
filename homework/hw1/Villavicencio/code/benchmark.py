import csv
import json
import time
import signal
from pathlib import Path

from search import bfs, dfs, ucs, ids, astar
from gridworld import GridProblem

from eight_puzzle import EightPuzzle

from heuristics import (
    h_misplaced,
    h_manhattan,
    h_manhattan_x3,
)

# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

HERE = Path(__file__).resolve().parent
RESULTS_DIR = HERE.parent / "results"

# Change this if your instances.json is directly inside code/
INSTANCES_FILE = HERE / "data" / "instances.json"
PUZZLE_INSTANCES_FILE = HERE / "data" / "puzzle_instances.json"

RESULTS_DIR.mkdir(exist_ok=True)


# ---------------------------------------------------------
# Grid heuristic
# ---------------------------------------------------------

def grid_manhattan(problem, state):
    """
    Manhattan distance for the weighted grid.

    Since the cheapest terrain cost is 1, ordinary Manhattan
    distance is an admissible lower bound on remaining cost.
    """
    r, c = state
    gr, gc = problem.goal

    return abs(r - gr) + abs(c - gc)


# ---------------------------------------------------------
# Run one algorithm
# ---------------------------------------------------------

class SearchTimeout(Exception):
    pass


def timeout_handler(signum, frame):
    raise SearchTimeout

TIMEOUT_SECONDS = 10

def run_algorithm(name, problem):
    """
    Run one search algorithm with a hard timeout.

    Returns the raw measurements required by the homework.
    """

    signal.signal(signal.SIGALRM, timeout_handler)
    signal.setitimer(signal.ITIMER_REAL, TIMEOUT_SECONDS)

    start_time = time.perf_counter()

    try:
        if name == "BFS":
            node, expansions, max_frontier = bfs(problem)

        elif name == "DFS":
            node, expansions, max_frontier = dfs(problem)

        elif name == "UCS":
            node, expansions, max_frontier = ucs(problem)

        elif name == "IDS":
            node, expansions, max_frontier = ids(problem)

        elif name == "A*_Manhattan":
            node, expansions, max_frontier = astar(
                problem,
                lambda state: grid_manhattan(problem, state)
            )

        else:
            raise ValueError(f"Unknown algorithm: {name}")

        elapsed = time.perf_counter() - start_time

        if node is None:
            return {
                "status": "failure",
                "cost": None,
                "length": None,
                "expansions": expansions,
                "max_frontier": max_frontier,
                "time_seconds": elapsed,
            }

        return {
            "status": "solved",
            "cost": node.g,
            "length": len(node.path()),
            "expansions": expansions,
            "max_frontier": max_frontier,
            "time_seconds": elapsed,
        }

    except SearchTimeout:
        elapsed = time.perf_counter() - start_time

        return {
            "status": "timeout",
            "cost": None,
            "length": None,
            "expansions": None,
            "max_frontier": None,
            "time_seconds": elapsed,
        }

    finally:
        # Always cancel the timer before running the next algorithm.
        signal.setitimer(signal.ITIMER_REAL, 0)

def run_puzzle_algorithm(name, problem):
    """
    Run one algorithm on an 8-puzzle instance
    using the same hard timeout as the grid benchmark.
    """

    signal.signal(signal.SIGALRM, timeout_handler)
    signal.setitimer(signal.ITIMER_REAL, TIMEOUT_SECONDS)

    start_time = time.perf_counter()

    try:
        if name == "BFS":
            node, expansions, max_frontier = bfs(problem)

        elif name == "DFS":
            node, expansions, max_frontier = dfs(problem)

        elif name == "UCS":
            node, expansions, max_frontier = ucs(problem)

        elif name == "IDS":
            node, expansions, max_frontier = ids(problem)

        elif name == "A*_Misplaced":
            node, expansions, max_frontier = astar(
                problem,
                h_misplaced
            )

        elif name == "A*_Manhattan":
            node, expansions, max_frontier = astar(
                problem,
                h_manhattan
            )

        elif name == "A*_Manhattan_x3":
            node, expansions, max_frontier = astar(
                problem,
                h_manhattan_x3
            )

        else:
            raise ValueError(
                f"Unknown puzzle algorithm: {name}"
            )

        elapsed = time.perf_counter() - start_time

        if node is None:
            return {
                "status": "failure",
                "cost": None,
                "length": None,
                "expansions": expansions,
                "max_frontier": max_frontier,
                "time_seconds": elapsed,
            }

        return {
            "status": "solved",
            "cost": node.g,
            "length": len(node.path()),
            "expansions": expansions,
            "max_frontier": max_frontier,
            "time_seconds": elapsed,
        }

    except SearchTimeout:
        elapsed = time.perf_counter() - start_time

        return {
            "status": "timeout",
            "cost": None,
            "length": None,
            "expansions": None,
            "max_frontier": None,
            "time_seconds": elapsed,
        }

    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)

# ---------------------------------------------------------
# Grid benchmark
# ---------------------------------------------------------

def benchmark_grids():

    with open(INSTANCES_FILE, "r") as f:
        data = json.load(f)

    algorithms = [
    "BFS",
    "DFS",
    "UCS",
    "IDS",
    "A*_Manhattan",
    ]

    rows = []

    for size in data["sizes"]:

        instances = data["instances"][str(size)]

        print(f"\n=== GRID {size}x{size} ===")

        for instance_id, grid in enumerate(instances):

            print(
                f"Instance {instance_id + 1}/{len(instances)}",
                end=": "
            )

            for algorithm in algorithms:

                problem = GridProblem(grid)

                result = run_algorithm(
                    algorithm,
                    problem
                )

                row = {
                    "domain": "grid",
                    "difficulty": size,
                    "instance": instance_id,
                    "algorithm": algorithm,
                    **result,
                }

                rows.append(row)

                print(
                    f"{algorithm}={result['status']}",
                    end="  "
                )

            print()

    return rows

def benchmark_puzzles():

    with open(PUZZLE_INSTANCES_FILE, "r") as f:
        data = json.load(f)

    algorithms = [
        "BFS",
        "DFS",
        "UCS",
        "IDS",
        "A*_Misplaced",
        "A*_Manhattan",
        "A*_Manhattan_x3",
    ]

    rows = []

    for depth in data["depths"]:

        instances = data["instances"][str(depth)]

        print(f"\n=== 8-PUZZLE DEPTH {depth} ===")

        for instance_id, state in enumerate(instances):

            # JSON stores arrays as lists.
            # Search states need to be hashable tuples.
            initial = tuple(state)

            print(
                f"Instance {instance_id + 1}/{len(instances)}",
                end=": "
            )

            for algorithm in algorithms:

                problem = EightPuzzle(initial)

                result = run_puzzle_algorithm(
                    algorithm,
                    problem
                )

                row = {
                    "domain": "8-puzzle",
                    "difficulty": depth,
                    "instance": instance_id,
                    "algorithm": algorithm,
                    **result,
                }

                rows.append(row)

                print(
                    f"{algorithm}={result['status']}",
                    end="  "
                )

            print()

    return rows

# ---------------------------------------------------------
# CSV
# ---------------------------------------------------------

def save_csv(rows, filename):

    if not rows:
        return

    output_file = RESULTS_DIR / filename

    fieldnames = [
        "domain",
        "difficulty",
        "instance",
        "algorithm",
        "status",
        "cost",
        "length",
        "expansions",
        "max_frontier",
        "time_seconds",
    ]

    with open(
        output_file,
        "w",
        newline=""
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(rows)

    print(f"\nSaved: {output_file}")


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

if __name__ == "__main__":

    puzzle_rows = benchmark_puzzles()

    save_csv(
        puzzle_rows,
        "puzzle_raw.csv"
    )