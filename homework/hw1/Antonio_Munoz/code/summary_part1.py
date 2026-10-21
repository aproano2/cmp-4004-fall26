"""Part 1 summary: median and IQR of every required metric, per domain x algorithm
x level (10 instances each), plus an overview figure.
Timeouts are reported AS timeouts (n_timeout). Statistics use only runs that
finished (n_ok); if >= half of the runs timed out, the median is NOT reported
(a median over survivors would be dishonest).
Reads ../results/classical_*.csv. Writes ../results/summary_part1.csv and
../fig/overview_expansions.png.   Run: python3 summary_part1.py"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).parent
RES, FIG = HERE.parent / "results", HERE.parent / "fig"
FIG.mkdir(exist_ok=True)
METRICS = ["cost", "length", "expansions", "max_frontier", "time_s"]

d = pd.concat([pd.read_csv(RES / "classical_8puzzle.csv"),
               pd.read_csv(RES / "classical_grid.csv")])
rows = []
for (dom, algo, level), g in d.groupby(["domain", "algo", "level"]):
    ok = g[g.status == "ok"]
    n_to = int((g.status == "timeout").sum())
    row = {"domain": dom, "algo": algo, "level": level, "n": len(g),
           "n_ok": len(ok), "n_timeout": n_to,
           "median_undefined": n_to * 2 >= len(g)}
    for m in METRICS:
        if row["median_undefined"] or len(ok) == 0:
            row[f"{m}_median"] = row[f"{m}_q1"] = row[f"{m}_q3"] = None
        else:
            row[f"{m}_median"] = ok[m].median()
            row[f"{m}_q1"] = ok[m].quantile(0.25)
            row[f"{m}_q3"] = ok[m].quantile(0.75)
    rows.append(row)
S = pd.DataFrame(rows)
S.to_csv(RES / "summary_part1.csv", index=False)

show = ["domain", "algo", "level", "n_ok", "n_timeout", "expansions_median",
        "max_frontier_median", "cost_median", "time_s_median"]
print(S[show].round(4).to_string(index=False))
print("\nTimeouts:\n", S[S.n_timeout > 0][["domain", "algo", "level", "n_timeout"]]
      .to_string(index=False))

# ---- overview figure: expansions vs level, log y, IQR bars ------------------
algos = {"8puzzle": ["bfs", "dfs", "ucs", "ids", "astar_misplaced", "astar_manhattan"],
         "grid": ["bfs", "dfs", "ucs", "ids", "astar_manhattan"]}
fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
for ax, dom in zip(axes, ["8puzzle", "grid"]):
    levels = sorted(S[S.domain == dom].level.unique())
    for k, a in enumerate(algos[dom]):
        s = S[(S.domain == dom) & (S.algo == a)].sort_values("level")
        s = s[~s.median_undefined]
        off = (k - len(algos[dom]) / 2) * 0.08 * (levels[-1] - levels[0]) / 12
        ax.errorbar(s.level + off, s.expansions_median,
                    yerr=[s.expansions_median - s.expansions_q1,
                          s.expansions_q3 - s.expansions_median],
                    marker="o", ms=4, capsize=2, label=a)
    for _, r in S[(S.domain == dom) & S.median_undefined].iterrows():
        ax.annotate(f"{r.algo}: timeout\n({int(r.n_timeout)}/{int(r.n)})",
                    (r.level, ax.get_ylim()[1]), ha="center", va="top",
                    fontsize=7, color="red")
    ax.set_yscale("log")
    ax.set_xticks(levels)
    ax.set_xlabel("solution depth" if dom == "8puzzle" else "grid size (n x n)")
    ax.set_ylabel("expansions (median, IQR bars)")
    ax.set_title({"8puzzle": "8-puzzle", "grid": "Weighted grid"}[dom])
    ax.legend(fontsize=7)
fig.tight_layout()
fig.savefig(FIG / "overview_expansions.png", dpi=150)
print("\nsaved fig/overview_expansions.png")
