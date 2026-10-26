import csv
import statistics
from pathlib import Path

from heuristics import effective_bf


HERE = Path(__file__).resolve().parent
RESULTS_DIR = HERE.parent / "results"

PUZZLE_RAW = RESULTS_DIR / "puzzle_raw.csv"
PUZZLE_SUMMARY = RESULTS_DIR / "puzzle_summary.csv"
GRID_RAW = RESULTS_DIR / "grid_raw.csv"
GRID_SUMMARY = RESULTS_DIR / "grid_summary.csv"


def load_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def percentile(values, p):
    """
    Simple linear-interpolation percentile.
    p should be between 0 and 1.
    """

    values = sorted(values)

    if not values:
        return None

    position = (len(values) - 1) * p

    lower = int(position)
    upper = min(lower + 1, len(values) - 1)

    fraction = position - lower

    return (
        values[lower]
        + fraction * (values[upper] - values[lower])
    )


def median_iqr(values):

    values = list(values)

    return {
        "median": statistics.median(values),
        "q1": percentile(values, 0.25),
        "q3": percentile(values, 0.75),
        "iqr": (
            percentile(values, 0.75)
            - percentile(values, 0.25)
        ),
    }


def add_effective_branching_factor(rows):

    for row in rows:

        if (
            row["status"] == "solved"
            and row["algorithm"] in (
                "A*_Misplaced",
                "A*_Manhattan",
            )
        ):
            expansions = int(row["expansions"])
            depth = int(row["length"])

            row["effective_bf"] = effective_bf(
                expansions,
                depth
            )

        else:
            row["effective_bf"] = None


def summarize(rows):

    summary = []

    depths = sorted({
        int(row["difficulty"])
        for row in rows
    })

    algorithms = sorted({
        row["algorithm"]
        for row in rows
    })

    for depth in depths:

        for algorithm in algorithms:

            group = [
                row
                for row in rows
                if int(row["difficulty"]) == depth
                and row["algorithm"] == algorithm
                and row["status"] == "solved"
            ]

            if not group:
                continue

            costs = [
                float(row["cost"])
                for row in group
            ]

            lengths = [
                float(row["length"])
                for row in group
            ]

            expansions = [
                float(row["expansions"])
                for row in group
            ]

            frontiers = [
                float(row["max_frontier"])
                for row in group
            ]

            times = [
                float(row["time_seconds"])
                for row in group
            ]

            cost_stats = median_iqr(costs)
            length_stats = median_iqr(lengths)
            expansion_stats = median_iqr(expansions)
            frontier_stats = median_iqr(frontiers)
            time_stats = median_iqr(times)

            bfs_values = [
                float(row["effective_bf"])
                for row in group
                if row["effective_bf"] is not None
            ]

            if bfs_values:
                bf_stats = median_iqr(bfs_values)
            else:
                bf_stats = {
                    "median": None,
                    "iqr": None,
                }

            summary.append({
                "depth": depth,
                "algorithm": algorithm,
                "n": len(group),

                "cost_median": cost_stats["median"],
                "cost_iqr": cost_stats["iqr"],

                "length_median": length_stats["median"],
                "length_iqr": length_stats["iqr"],

                "expansions_median": expansion_stats["median"],
                "expansions_iqr": expansion_stats["iqr"],

                "max_frontier_median": frontier_stats["median"],
                "max_frontier_iqr": frontier_stats["iqr"],

                "time_median": time_stats["median"],
                "time_iqr": time_stats["iqr"],

                "effective_bf_median": bf_stats["median"],
                "effective_bf_iqr": bf_stats["iqr"],
            })

    return summary


def save_summary(rows):

    fieldnames = [
        "depth",
        "algorithm",
        "n",
        "cost_median",
        "cost_iqr",
        "length_median",
        "length_iqr",
        "expansions_median",
        "expansions_iqr",
        "max_frontier_median",
        "max_frontier_iqr",
        "time_median",
        "time_iqr",
        "effective_bf_median",
        "effective_bf_iqr",
    ]

    with open(
        PUZZLE_SUMMARY,
        "w",
        newline=""
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(rows)

def summarize_grids(rows):
    """
    Summarize grid results by size and algorithm.

    Reports medians/IQRs over solved runs and separately
    reports timeout counts.
    """

    summary = []

    sizes = sorted({
        int(row["difficulty"])
        for row in rows
    })

    algorithms = sorted({
        row["algorithm"]
        for row in rows
    })

    for size in sizes:

        for algorithm in algorithms:

            all_runs = [
                row
                for row in rows
                if int(row["difficulty"]) == size
                and row["algorithm"] == algorithm
            ]

            solved = [
                row
                for row in all_runs
                if row["status"] == "solved"
            ]

            timeouts = [
                row
                for row in all_runs
                if row["status"] == "timeout"
            ]

            result = {
                "size": size,
                "algorithm": algorithm,
                "n": len(all_runs),
                "solved": len(solved),
                "timeouts": len(timeouts),
                "timeout_rate": (
                    len(timeouts) / len(all_runs)
                    if all_runs
                    else 0
                ),
            }

            if solved:

                metrics = {
                    "cost": [
                        float(row["cost"])
                        for row in solved
                    ],
                    "length": [
                        float(row["length"])
                        for row in solved
                    ],
                    "expansions": [
                        float(row["expansions"])
                        for row in solved
                    ],
                    "max_frontier": [
                        float(row["max_frontier"])
                        for row in solved
                    ],
                    "time": [
                        float(row["time_seconds"])
                        for row in solved
                    ],
                }

                for metric, values in metrics.items():

                    stats = median_iqr(values)

                    result[f"{metric}_median"] = stats["median"]
                    result[f"{metric}_iqr"] = stats["iqr"]

            summary.append(result)

    return summary


def save_grid_summary(rows):

    fieldnames = [
        "size",
        "algorithm",
        "n",
        "solved",
        "timeouts",
        "timeout_rate",
        "cost_median",
        "cost_iqr",
        "length_median",
        "length_iqr",
        "expansions_median",
        "expansions_iqr",
        "max_frontier_median",
        "max_frontier_iqr",
        "time_median",
        "time_iqr",
    ]

    with open(
        GRID_SUMMARY,
        "w",
        newline=""
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames,
            extrasaction="ignore"
        )

        writer.writeheader()
        writer.writerows(rows)

def main():

    # -------------------------
    # 8-puzzle
    # -------------------------

    puzzle_rows = load_csv(PUZZLE_RAW)

    add_effective_branching_factor(
        puzzle_rows
    )

    puzzle_summary = summarize(
        puzzle_rows
    )

    save_summary(
        puzzle_summary
    )

    print(
        f"Loaded {len(puzzle_rows)} puzzle measurements."
    )

    print(
        f"Saved: {PUZZLE_SUMMARY}"
    )

    print("\nEffective branching factor:")

    for row in puzzle_summary:

        if row["algorithm"] in (
            "A*_Misplaced",
            "A*_Manhattan",
        ):

            print(
                f"Depth {row['depth']:2} | "
                f"{row['algorithm']:15} | "
                f"median b* = "
                f"{row['effective_bf_median']:.4f} | "
                f"IQR = "
                f"{row['effective_bf_iqr']:.4f}"
            )

    # -------------------------
    # Grid
    # -------------------------

    grid_rows = load_csv(
        GRID_RAW
    )

    grid_summary = summarize_grids(
        grid_rows
    )

    save_grid_summary(
        grid_summary
    )

    print()
    print(
        f"Loaded {len(grid_rows)} grid measurements."
    )

    print(
        f"Saved: {GRID_SUMMARY}"
    )

    print("\nGrid timeout summary:")

    for row in grid_summary:

        if row["timeouts"] > 0:

            print(
                f"{row['size']}x{row['size']} | "
                f"{row['algorithm']} | "
                f"{row['timeouts']}/{row['n']} "
                f"timeouts"
            )


if __name__ == "__main__":
    main()