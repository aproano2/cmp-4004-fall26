"""
Genera las figuras de la Parte 1

Los datos salen de: results/classical_results.csv
Las figuras se guardan en: fig/
"""

from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd


CODE_DIR = Path(__file__).resolve().parent
HW1_DIR = CODE_DIR.parent

RESULTS_FILE = HW1_DIR / "results" / "classical_results.csv"
FIG_DIR = HW1_DIR / "fig"


def load_results():
    return pd.read_csv(RESULTS_FILE)


def median_iqr(data, value_column):
    median = data[value_column].median()
    q1 = data[value_column].quantile(0.25)
    q3 = data[value_column].quantile(0.75)

    return median, q1, q3


def effective_bf(N, d, lo=1.0000001, hi=10.0, tol=1e-6):

    if d == 0:
        return 0.0

    #Bisección usada en Week 4 para aproximar b*
    while hi - lo > tol:
        mid = (lo + hi) / 2

        total = sum(
            mid ** i
            for i in range(d + 1)
        )

        if total < N + 1:
            lo = mid
        else:
            hi = mid

    return (lo + hi) / 2


def figure_puzzle_expansions(df):

    puzzle = df[
        (df["domain"] == "8puzzle")
        & (df["status"] == "solved")
    ].copy()

    configurations = [
        ("BFS", "", "BFS"),
        ("DFS", "", "DFS"),
        ("UCS", "", "UCS"),
        ("IDS", "", "IDS"),
        ("A*", "manhattan", "A* Manhattan"),
    ]

    plt.figure(figsize=(9, 6))

    for algorithm, heuristic, label in configurations:

        if algorithm == "A*":
            current = puzzle[
                (puzzle["algorithm"] == algorithm)
                & (puzzle["heuristic"] == heuristic)
            ]
        else:
            current = puzzle[
                puzzle["algorithm"] == algorithm
            ]

        levels = []
        medians = []
        lower_errors = []
        upper_errors = []

        for level in sorted(current["level"].unique()):

            level_data = current[
                current["level"] == level
            ]

            median, q1, q3 = median_iqr(
                level_data,
                "expansions"
            )

            levels.append(level)
            medians.append(median)
            lower_errors.append(median - q1)
            upper_errors.append(q3 - median)

        plt.errorbar(
            levels,
            medians,
            yerr=[
                lower_errors,
                upper_errors
            ],
            marker="o",
            capsize=4,
            label=label
        )

    #La escala log ayuda a comparar algoritmos con diferencias grandes de expansiones
    plt.yscale("log")

    plt.xlabel("Profundidad del 8-puzzle")
    plt.ylabel("Expansiones - mediana e IQR")
    plt.title("Expansiones por dificultad en 8-puzzle")

    plt.xticks([4, 8, 12, 16])
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    output = FIG_DIR / "fig1_puzzle_expansions.png"
    plt.savefig(output, dpi=200)
    plt.close()

    print("Creada:", output)


def figure_grid_time(df):

    grid = df[
        (df["domain"] == "grid")
        & (df["status"] == "solved")
    ].copy()

    configurations = [
        ("BFS", "", "BFS"),
        ("DFS", "", "DFS"),
        ("UCS", "", "UCS"),
        ("IDS", "", "IDS"),
        ("A*", "manhattan_scaled", "A* Manhattan"),
    ]

    plt.figure(figsize=(9, 6))

    for algorithm, heuristic, label in configurations:

        if algorithm == "A*":
            current = grid[
                (grid["algorithm"] == algorithm)
                & (grid["heuristic"] == heuristic)
            ]
        else:
            current = grid[
                grid["algorithm"] == algorithm
            ]

        levels = []
        medians = []
        lower_errors = []
        upper_errors = []

        for level in sorted(current["level"].unique()):

            level_data = current[
                current["level"] == level
            ]

            median, q1, q3 = median_iqr(
                level_data,
                "wall_time_sec"
            )

            levels.append(level)
            medians.append(median)
            lower_errors.append(median - q1)
            upper_errors.append(q3 - median)

        plt.errorbar(
            levels,
            medians,
            yerr=[
                lower_errors,
                upper_errors
            ],
            marker="o",
            capsize=4,
            label=label
        )

    #Hay diferencias grandes de tiempo, sobre todo con IDS
    plt.yscale("log")

    plt.xlabel("Tamaño del grid")
    plt.ylabel("Tiempo en segundos - mediana e IQR")
    plt.title("Tiempo por dificultad en weighted grid")

    plt.xticks([5, 8, 12, 16])
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    output = FIG_DIR / "fig2_grid_time.png"
    plt.savefig(output, dpi=200)
    plt.close()

    print("Creada:", output)


def figure_heuristics(df):

    puzzle = df[
        (df["domain"] == "8puzzle")
        & (df["algorithm"] == "A*")
        & (df["status"] == "solved")
        & (
            df["heuristic"].isin(
                ["misplaced", "manhattan"]
            )
        )
    ].copy()

    heuristics = [
        ("misplaced", "Misplaced tiles"),
        ("manhattan", "Manhattan"),
    ]

    plt.figure(figsize=(8, 6))

    for heuristic, label in heuristics:

        current = puzzle[
            puzzle["heuristic"] == heuristic
        ]

        levels = []
        medians = []
        lower_errors = []
        upper_errors = []

        for level in sorted(current["level"].unique()):

            level_data = current[
                current["level"] == level
            ]

            median, q1, q3 = median_iqr(
                level_data,
                "expansions"
            )

            levels.append(level)
            medians.append(median)
            lower_errors.append(median - q1)
            upper_errors.append(q3 - median)

        plt.errorbar(
            levels,
            medians,
            yerr=[
                lower_errors,
                upper_errors
            ],
            marker="o",
            capsize=4,
            label=label
        )

    plt.yscale("log")

    plt.xlabel("Profundidad del 8-puzzle")
    plt.ylabel("Expansiones - mediana e IQR")
    plt.title("A*: Misplaced tiles vs Manhattan")

    plt.xticks([4, 8, 12, 16])
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    output = FIG_DIR / "fig3_heuristics.png"
    plt.savefig(output, dpi=200)
    plt.close()

    print("Creada:", output)


def figure_effective_branching_factor(df):

    puzzle = df[
        (df["domain"] == "8puzzle")
        & (df["algorithm"] == "A*")
        & (df["status"] == "solved")
        & (
            df["heuristic"].isin(
                ["zero", "misplaced", "manhattan", "manhattan_x3"]
            )
        )
    ].copy()

    puzzle["b_star"] = puzzle.apply(
        lambda row: effective_bf(
            row["expansions"],
            int(row["solution_length"])
        ),
        axis=1
    )

    heuristics = [
        ("zero", "h = 0"),
        ("misplaced", "Misplaced tiles"),
        ("manhattan", "Manhattan"),
        ("manhattan_x3", "Manhattan x3"),
    ]

    plt.figure(figsize=(9, 6))

    for heuristic, label in heuristics:

        current = puzzle[
            puzzle["heuristic"] == heuristic
        ]

        levels = []
        medians = []
        lower_errors = []
        upper_errors = []

        for level in sorted(current["level"].unique()):

            level_data = current[
                current["level"] == level
            ]

            median, q1, q3 = median_iqr(
                level_data,
                "b_star"
            )

            levels.append(level)
            medians.append(median)
            lower_errors.append(median - q1)
            upper_errors.append(q3 - median)

        plt.errorbar(
            levels,
            medians,
            yerr=[
                lower_errors,
                upper_errors
            ],
            marker="o",
            capsize=4,
            label=label
        )

    plt.xlabel("Profundidad del 8-puzzle")
    plt.ylabel("Effective branching factor b*")
    plt.title("Effective branching factor de A*")

    plt.xticks([4, 8, 12, 16])
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    output = FIG_DIR / "fig4_effective_bf.png"
    plt.savefig(output, dpi=200)
    plt.close()

    print("Creada:", output)

def save_classical_summary(df):
    solved = df[df["status"] == "solved"].copy()

    metrics = [
        "solution_cost",
        "solution_length",
        "expansions",
        "max_frontier",
        "wall_time_sec",
    ]

    group_cols = [
        "domain",
        "level",
        "algorithm",
        "heuristic",
    ]

    summary = (
        solved
        .groupby(group_cols, dropna=False)[metrics]
        .quantile([0.25, 0.5, 0.75])
        .unstack(-1)
    )

    labels = {
        0.25: "q1",
        0.5: "median",
        0.75: "q3",
    }

    summary.columns = [
        f"{metric}_{labels[q]}"
        for metric, q in summary.columns
    ]

    summary = summary.reset_index()

    output = HW1_DIR / "results" / "classical_summary.csv"
    summary.to_csv(output, index=False)

    print("Creado:", output)

def main():

    FIG_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    print("Leyendo resultados...")
    df = load_results()

    print("Filas encontradas:", len(df))
    print()

    save_classical_summary(df)

    figure_puzzle_expansions(df)
    figure_grid_time(df)
    figure_heuristics(df)
    figure_effective_branching_factor(df)

    print()
    print("Figuras terminadas")


if __name__ == "__main__":
    main()