import csv
from collections import Counter
from pathlib import Path
from statistics import mean, stdev

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = Path(__file__).resolve().parents[1]
with (BASE / "results/results.csv").open(encoding="utf-8", newline="") as file:
    rows = list(csv.DictReader(file))
assert len(rows) == 240
assert len({(r["repeat"], r["problem_id"], r["arm"]) for r in rows}) == 240
OUT = BASE / "fig"
OUT.mkdir(exist_ok=True)
plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})


def save(fig, name, note):
    fig.text(0.02, 0.02, note, fontsize=9, color="#475569")
    fig.tight_layout(rect=(0, 0.09, 1, 1))
    fig.savefig(OUT / name, dpi=180, facecolor="white")
    plt.close(fig)
    print(name)


levels = ("facil", "medio", "dificil")
repeats = sorted({r["repeat"] for r in rows})
fig, ax = plt.subplots(figsize=(9, 5))
for index, (arm, label, color) in enumerate((
    ("A", "A: referencia + solver", "#2563eb"),
    ("B", "B: IA + solver", "#64748b"),
    ("Bp", "B': refinamiento", "#15803d"),
    ("C", "C: IA directa", "#d97706"),
)):
    values, deviations = [], []
    for level in levels:
        scores = []
        for repeat in repeats:
            group = [r for r in rows if (r["arm"], r["difficulty"], r["repeat"]) == (arm, level, repeat)]
            scores.append(100 * sum(r["status"] == "correct" for r in group) / len(group))
        values.append(mean(scores))
        deviations.append(stdev(scores))
    positions = [i + (index - 1.5) * 0.2 for i in range(3)]
    bars = ax.bar(positions, values, width=0.18, color=color, label=label, yerr=deviations, capsize=3)
    for bar, value, deviation in zip(bars, values, deviations):
        ax.text(bar.get_x() + bar.get_width() / 2, value + deviation + 2, f"{value:.1f}", ha="center", fontsize=9)
ax.set(title="Exactitud de respuestas por dificultad", ylabel="Respuestas correctas (%)", ylim=(0, 115))
ax.set_xticks(range(3), ["Facil (7 problemas)", "Medio (7 problemas)", "Dificil (6 problemas)"])
ax.legend(loc="upper right", fontsize=9)
save(fig, "accuracy_difficulty.png", "Media y desviacion estandar de 3 repeticiones. Se evalua la respuesta, no la fidelidad del modelo formal.")

failures = [r for r in rows if r["arm"] == "B" and r["status"] != "correct"]
syntax = sum(r["error"].startswith("parse_error:") for r in failures)
fig, ax = plt.subplots(figsize=(8, 3.5))
bars = ax.barh(["Sintaxis / formato", "Otros fallos primarios"], [syntax, len(failures) - syntax], color=["#d97706", "#64748b"])
ax.bar_label(bars, padding=5)
ax.invert_yaxis()
ax.set(title="Fallos del brazo B", xlabel="Numero de ejecuciones", xlim=(0, 70))
save(fig, "b_errors.png", f"{syntax}/{len(failures)} fallos detectados por el validador de formato. No se cuentan errores semanticos secundarios.")

refined = [r for r in rows if r["arm"] == "Bp"]
success = Counter(int(r["success_iteration"]) for r in refined if r["status"] == "correct")
wrong = sum(r["status"] == "incorrect" for r in refined)
missing = sum(r["status"] == "no-answer" for r in refined)
fig, ax = plt.subplots(figsize=(9, 5))
bars = ax.bar(range(4), [success[i] for i in range(4)], color="#15803d", label="Respuesta correcta")
ax.bar_label(bars, padding=4)
ax.bar(4, missing, color="#d97706", label="Sin respuesta valida")
ax.bar(4, wrong, bottom=missing, color="#b91c1c", label="Respuesta incorrecta")
ax.text(4, missing / 2, str(missing), ha="center", va="center", color="white", weight="bold")
ax.text(4, missing + wrong / 2, str(wrong), ha="center", va="center", color="white", weight="bold")
ax.set_xticks(range(5), ["Inicial (0)", "1", "2", "3", "Sin acierto"])
ax.set(title="B': reintentos hasta una respuesta correcta", xlabel="Numero de reintentos", ylabel="Numero de ejecuciones", ylim=(0, 63))
ax.legend(loc="upper left", fontsize=9)
save(fig, "refinement_iterations.png", "4/60 respuestas correctas, todas con modelos subrestringidos. 56/60 casos sin acierto (93.33%).")
