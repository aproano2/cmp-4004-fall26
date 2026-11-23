import csv
from pathlib import Path
from statistics import median

SUBMISSION = Path(__file__).resolve().parents[1]
ARMS = ("A", "B", "B′", "C")
DIFFICULTIES = ("easy", "medium", "hard")
OUTCOMES = ("correct", "incorrect", "no-answer")


def load_results():
    expected = {}
    groups = {}

    for arm, filename in zip(
        ARMS, ("arm_a.csv", "arm_b.csv", "arm_b_prime.csv", "arm_c.csv")
    ):
        path = SUBMISSION / "results" / filename
        if not path.exists():
            raise SystemExit(f"Falta results/{filename}.")

        with path.open(encoding="utf-8-sig", newline="") as file:
            rows = list(csv.DictReader(file))

        instances = {row["problem_id"]: row["difficulty"] for row in rows}
        if arm == "A":
            expected = instances

        required_ids = {f"sat_{number:02d}" for number in range(1, 21)}
        if (
            len(rows) != 20
            or set(instances) != required_ids
            or instances != expected
            or set(instances.values()) != set(DIFFICULTIES)
        ):
            raise SystemExit(f"{filename}: revisa los 20 IDs y sus dificultades.")
        if any(row["outcome"] not in OUTCOMES for row in rows):
            raise SystemExit(f"{filename}: revisa los valores de outcome.")

        groups[arm] = rows

    return groups


def save(fig, folder, name):
    fig.tight_layout()
    fig.savefig(folder / name, dpi=180, bbox_inches="tight")


def main():
    groups = load_results()
    import matplotlib.pyplot as plt

    folder = SUBMISSION / "fig"
    folder.mkdir(exist_ok=True)

    fig, ax = plt.subplots()
    for arm, rows in groups.items():
        accuracy = []
        for level in DIFFICULTIES:
            level_rows = [row for row in rows if row["difficulty"] == level]
            correct = sum(row["outcome"] == "correct" for row in level_rows)
            accuracy.append(100 * correct / len(level_rows))
        ax.plot(["Fácil", "Intermedio", "Difícil"], accuracy, marker="o", label=arm)
    ax.set(ylabel="Exactitud (%)", ylim=(0, 105), title="Exactitud por dificultad")
    ax.legend(title="Brazo")
    save(fig, folder, "accuracy_by_difficulty.png")
    plt.close(fig)

    fig, ax = plt.subplots()
    bottom = [0] * len(ARMS)
    for outcome, label in zip(OUTCOMES, ("Correcta", "Incorrecta", "Sin respuesta")):
        counts = [
            sum(row["outcome"] == outcome for row in groups[arm])
            for arm in ARMS
        ]
        ax.bar(ARMS, counts, bottom=bottom, label=label)
        bottom = [previous + count for previous, count in zip(bottom, counts)]
    ax.set(xlabel="Brazo", ylabel="Número de problemas", title="Resultados por brazo")
    ax.legend()
    save(fig, folder, "outcomes_by_arm.png")
    plt.close(fig)

    fig, ax = plt.subplots()
    for offset, field, label in (
        (-0.25, "wall_ms", "Total"),
        (0, "solver_ms", "Solver"),
        (0.25, "llm_ms", "LLM"),
    ):
        positions, values = [], []
        for index, arm in enumerate(ARMS):
            measured = [float(row[field]) for row in groups[arm] if row[field].strip()]
            if measured:
                positions.append(index + offset)
                values.append(median(measured))
        if values:
            ax.bar(positions, values, width=0.23, label=label)
    ax.set_xticks(range(len(ARMS)))
    ax.set_xticklabels(ARMS)
    ax.set(xlabel="Brazo", ylabel="Mediana (ms)", title="Tiempo por brazo")
    ax.set_yscale("symlog", linthresh=1)
    ax.legend()
    save(fig, folder, "median_time_by_arm.png")
    plt.close(fig)

    print(f"Tres gráficas guardadas en {folder}")


if __name__ == "__main__":
    main()