"""Figuras del reporte. Se corre después de benchmark.py (y otra vez después de duel.py):

    python code/plots.py
"""
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
RESULTS, FIG = ROOT / "results", ROOT / "fig"
FIG.mkdir(exist_ok=True)

COLORS = {"BFS": "#4477AA", "DFS": "#EE6677", "UCS": "#228833", "IDS": "#CCBB44",
          "A*-misplaced": "#66CCEE", "A*-manhattan": "#AA3377",
          "A*-3xmanhattan": "#888888",
          "classical": "#AA3377", "llm": "#EE6677", "tool": "#4477AA"}
TITLES = {"puzzle": "8-puzzle (profundidad óptima)", "grid": "Grid con pesos (lado n)"}
plt.rcParams.update({"font.size": 10, "axes.spines.top": False,
                     "axes.spines.right": False, "figure.dpi": 150})


def read(name):
    with open(RESULTS / name, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save(fig, name):
    fig.tight_layout()
    fig.savefig(FIG / name, bbox_inches="tight")
    plt.close(fig)
    print(f"  escrito fig/{name}")


def fig_scaling():
    rows = read("classical_summary.csv")
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    for ax, domain in zip(axes, ("puzzle", "grid")):
        algos = []
        for r in rows:
            if r["domain"] == domain and r["algorithm"] not in algos \
                    and r["algorithm"] != "A*-3xmanhattan":
                algos.append(r["algorithm"])
        for a in algos:
            rs = sorted((r for r in rows if r["domain"] == domain
                         and r["algorithm"] == a and r["expansions_median"]),
                        key=lambda r: int(r["level"]))
            x = [int(r["level"]) for r in rs]
            med = np.array([float(r["expansions_median"]) for r in rs])
            q1 = np.array([float(r["expansions_q1"]) for r in rs])
            q3 = np.array([float(r["expansions_q3"]) for r in rs])
            ax.errorbar(x, med, yerr=[med - q1, q3 - med], marker="o", capsize=3,
                        color=COLORS[a], label=a, lw=1.6)
            for r, xv, mv in zip(rs, x, med):
                if int(r["n_timeout"]):
                    ax.annotate(f"{r['n_timeout']}/{r['n']} timeouts",
                                (xv, mv), textcoords="offset points",
                                xytext=(-62, 6), fontsize=8, color=COLORS[a])
        ax.set_yscale("log")
        ax.set_xticks(x)
        ax.set_xlabel(TITLES[domain])
        ax.set_ylabel("nodos expandidos (mediana, barras = IQR)")
        ax.set_title(domain)
        ax.legend(fontsize=8, frameon=False)
    save(fig, "fig1_expansions_scaling.png")


def fig_heuristics():
    dom, ebf = read("dominance.csv"), read("ebf.csv")
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    ax = axes[0]
    for lv, mk in zip((4, 8, 12, 16), "osD^"):
        pts = [(int(r["expansions_misplaced"]), int(r["expansions_manhattan"]))
               for r in dom if int(r["level"]) == lv]
        ax.scatter(*zip(*pts), marker=mk, label=f"profundidad {lv}", alpha=.8,
                   color=COLORS["A*-manhattan"], edgecolor="k", lw=.4)
    lim = [1, max(int(r["expansions_misplaced"]) for r in dom) * 1.5]
    ax.plot(lim, lim, "k--", lw=1, label="y = x")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("expansiones, A* + fichas mal ubicadas")
    ax.set_ylabel("expansiones, A* + Manhattan")
    ax.set_title("Dominancia: ningún punto sobre la diagonal")
    ax.legend(fontsize=8, frameon=False)

    ax = axes[1]
    for h in ("A*-misplaced", "A*-manhattan"):
        x, med, lo, hi = [], [], [], []
        for lv in (4, 8, 12, 16):
            v = [float(r["b_star"]) for r in ebf if r["domain"] == "puzzle"
                 and r["heuristic"] == h and int(r["level"]) == lv]
            q1, m, q3 = np.percentile(v, [25, 50, 75])
            x.append(lv); med.append(m); lo.append(m - q1); hi.append(q3 - m)
        ax.errorbar(x, med, yerr=[lo, hi], marker="o", capsize=3,
                    color=COLORS[h], label=h, lw=1.6)
    ax.set_xticks([4, 8, 12, 16])
    ax.set_xlabel("profundidad óptima del 8-puzzle")
    ax.set_ylabel("factor de ramificación efectivo b* (mediana, IQR)")
    ax.set_title("b* por heurística")
    ax.legend(fontsize=8, frameon=False)
    save(fig, "fig2_heuristics.png")


def fig_weighted():
    rows = read("weighted_astar.csv")
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    for col, ylabel, title in (
            ("expansion_speedup", "expansiones(h) / expansiones(3h)",
             "Aceleración al romper la admisibilidad"),
            ("cost_ratio", "costo(3h) / costo óptimo", "Precio en calidad de la solución")):
        ax = axes[0] if col == "expansion_speedup" else axes[1]
        for domain, color in (("puzzle", "#AA3377"), ("grid", "#228833")):
            x, med, lo, hi = [], [], [], []
            for lv in (4, 5, 8, 12, 16):
                v = [float(r[col]) for r in rows if r["domain"] == domain
                     and int(r["level"]) == lv]
                if not v:
                    continue
                q1, m, q3 = np.percentile(v, [25, 50, 75])
                x.append(lv); med.append(m); lo.append(m - q1); hi.append(q3 - m)
            ax.errorbar(x, med, yerr=[lo, hi], marker="o", capsize=3, color=color,
                        label=domain, lw=1.6)
        ax.axhline(1, color="k", ls="--", lw=1)
        ax.set_xlabel("nivel de dificultad (profundidad del puzzle / lado del grid)")
        ax.set_ylabel(ylabel + " (mediana, IQR)")
        ax.set_title(title)
        ax.legend(fontsize=8, frameon=False)
    save(fig, "fig3_weighted_astar.png")


def fig_duel():
    if not (RESULTS / "duel_runs.csv").exists():
        print("  (todavía no hay duel_runs.csv: corre code/duel.py para las figuras 4 y 5)")
        return
    rows = read("duel_runs.csv")
    labels = {"classical": "A* (clásico)", "llm": "LLM solo", "tool": "LLM + herramienta A*"}

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
    for ax, domain in zip(axes, ("puzzle", "grid")):
        levels = sorted({int(r["level"]) for r in rows if r["domain"] == domain})
        for arm, off in (("classical", 0), ("llm", -.12), ("tool", .12)):
            rate = []
            for lv in levels:
                rs = [r for r in rows if r["domain"] == domain and r["arm"] == arm
                      and int(r["level"]) == lv]
                rate.append(100 * sum(r["category"] in ("correct", "wrong_cost")
                                      for r in rs) / len(rs))
            ax.plot([lv + off for lv in levels], rate, marker="o", lw=1.8,
                    color=COLORS[arm], label=labels[arm])
        ax.set_xticks(levels)
        ax.set_ylim(-5, 105)
        ax.set_xlabel(TITLES[domain])
        ax.set_title(domain)
    axes[0].set_ylabel("instancias con camino legal Y óptimo (%)")
    axes[0].legend(fontsize=8, frameon=False)
    save(fig, "fig4_duel_scaling.png")

    cats = ["correct", "wrong_cost", "suboptimal", "illegal", "no_answer"]
    ccol = ["#228833", "#CCBB44", "#EE7733", "#CC3311", "#BBBBBB"]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
    for ax, arm in zip(axes, ("llm", "tool")):
        groups = [(d, lv) for d in ("puzzle", "grid")
                  for lv in sorted({int(r["level"]) for r in rows if r["domain"] == d})]
        bottom = np.zeros(len(groups))
        for cat, color in zip(cats, ccol):
            h = np.array([sum(r["arm"] == arm and r["domain"] == d
                              and int(r["level"]) == lv and r["category"] == cat
                              for r in rows) for d, lv in groups])
            ax.bar(range(len(groups)), h, bottom=bottom, color=color, label=cat)
            bottom += h
        ax.set_xticks(range(len(groups)))
        ax.set_xticklabels([f"{d[0].upper()}{lv}" for d, lv in groups])
        ax.set_xlabel("P = profundidad del puzzle, G = lado del grid")
        ax.set_title(labels[arm])
    axes[0].set_ylabel("instancias")
    axes[1].legend(fontsize=8, frameon=False, bbox_to_anchor=(1, 1))
    save(fig, "fig5_duel_failures.png")


if __name__ == "__main__":
    fig_scaling()
    fig_heuristics()
    fig_weighted()
    fig_duel()
