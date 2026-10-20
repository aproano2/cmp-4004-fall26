import csv
from pathlib import Path

import matplotlib.pyplot as plt


HERE = Path(__file__).resolve().parent
RESULTS_DIR = HERE.parent / "results"
FIG_DIR = HERE.parent / "fig"

PUZZLE_SUMMARY = RESULTS_DIR / "puzzle_summary.csv"

FIG_DIR.mkdir(exist_ok=True)


def load_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def plot_puzzle_expansions(rows):
    algorithms = [
        "BFS",
        "UCS",
        "IDS",
        "A*_Misplaced",
        "A*_Manhattan",
    ]

    depths = [4, 8, 12, 16]

    plt.figure(figsize=(8, 5))

    for algorithm in algorithms:
        algorithm_rows = {
            int(row["depth"]): row
            for row in rows
            if row["algorithm"] == algorithm
        }

        medians = [
            float(algorithm_rows[depth]["expansions_median"])
            for depth in depths
        ]

        plt.plot(
            depths,
            medians,
            marker="o",
            label=algorithm,
        )

    plt.yscale("log")
    plt.xlabel("Optimal solution depth")
    plt.ylabel("Median node expansions (log scale)")
    plt.title("8-Puzzle Search Scaling")
    plt.xticks(depths)
    plt.legend()
    plt.tight_layout()

    output = FIG_DIR / "puzzle_expansions.png"
    plt.savefig(output, dpi=200)
    plt.close()


def plot_effective_bf(rows):
    algorithms = [
        "A*_Misplaced",
        "A*_Manhattan",
    ]

    depths = [4, 8, 12, 16]

    plt.figure(figsize=(8, 5))

    for algorithm in algorithms:
        algorithm_rows = {
            int(row["depth"]): row
            for row in rows
            if row["algorithm"] == algorithm
        }

        medians = [
            float(
                algorithm_rows[depth]["effective_bf_median"]
            )
            for depth in depths
        ]

        plt.plot(
            depths,
            medians,
            marker="o",
            label=algorithm,
        )

    plt.xlabel("Optimal solution depth")
    plt.ylabel("Effective branching factor b*")
    plt.title("A* Heuristic Quality on the 8-Puzzle")
    plt.xticks(depths)
    plt.legend()
    plt.tight_layout()

    output = FIG_DIR / "heuristic_branching_factor.png"
    plt.savefig(output, dpi=200)
    plt.close()


def plot_inadmissible_tradeoff(rows):
    depth = 16

    algorithms = [
        "A*_Manhattan",
        "A*_Manhattan_x3",
    ]

    labels = [
        "Manhattan",
        "Manhattan ×3",
    ]

    algorithm_rows = {
        row["algorithm"]: row
        for row in rows
        if int(row["depth"]) == depth
    }

    expansions = [
        float(
            algorithm_rows[algorithm]["expansions_median"]
        )
        for algorithm in algorithms
    ]

    optimality = [
        "10/10 optimal",
        "7/10 optimal",
    ]

    plt.figure(figsize=(7, 5))

    bars = plt.bar(labels, expansions)

    plt.ylabel("Median node expansions")
    plt.title("Speed–Optimality Trade-off at Depth 16")

    for bar, value, optimality_text in zip(
        bars,
        expansions,
        optimality,
    ):
        x = bar.get_x() + bar.get_width() / 2

        plt.text(
            x,
            value,
            f"{value:g}",
            ha="center",
            va="bottom",
        )

        plt.text(
            x,
            value * 0.5,
            optimality_text,
            ha="center",
            va="center",
        )

    plt.tight_layout()

    output = FIG_DIR / "inadmissible_tradeoff.png"
    plt.savefig(output, dpi=200)
    plt.close()


def main():
    puzzle_rows = load_csv(PUZZLE_SUMMARY)

    plot_puzzle_expansions(puzzle_rows)
    plot_effective_bf(puzzle_rows)
    plot_inadmissible_tradeoff(puzzle_rows)


if __name__ == "__main__":
    main()