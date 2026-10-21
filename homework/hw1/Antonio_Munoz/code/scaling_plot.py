"""scaling_plot.py -- optimality rate vs problem size (scorecard axis 6).

Rate = share of instances whose PATH is legal AND optimal (categories `correct` +
`wrong_cost`: the path is optimal even if the model summed its cost wrong).
Error bars: Wilson 95% confidence interval for a proportion (n = 10 per size, so a
0/10 is compatible with a true rate of up to ~28%).
Systems: classical A* (from classical_grid.csv), the LLM (llm_grid.csv) and, if the
file exists, the tool-augmented arm (tool_grid.csv).
Writes ../fig/scaling.png and ../results/scaling_summary.csv.   Run: python3 scaling_plot.py
"""
from math import sqrt
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).parent
RES, FIG = HERE.parent / "results", HERE.parent / "fig"
SIZES = [5, 8, 12, 16]
OPTIMAL = {"correct", "wrong_cost"}


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


systems = {}

# classical A*: optimal iff it finished AND its cost equals UCS's (independent optimum)
c = pd.read_csv(RES / "classical_grid.csv")
w = c.pivot_table(index=["level", "instance"], columns="algo", values="cost", aggfunc="first")
systems["A* (classical)"] = {s: (int((w.loc[s]["astar_manhattan"] == w.loc[s]["ucs"]).sum()),
                                 len(w.loc[s])) for s in SIZES}

llm = pd.read_csv(RES / "llm_grid.csv")
systems["LLM qwen2.5:3b (direct)"] = {
    s: (int(llm[llm["size"] == s].category.isin(OPTIMAL).sum()),
        int((llm["size"] == s).sum())) for s in SIZES}

tool = RES / "tool_grid.csv"
if tool.exists():
    t = pd.read_csv(tool)
    systems["LLM + A* tool"] = {
        s: (int(t[t["size"] == s].category.isin(OPTIMAL).sum()),
            int((t["size"] == s).sum())) for s in SIZES}

rows, fig = [], plt.figure(figsize=(6.4, 4.2))
ax = fig.gca()
for k, (name, d) in enumerate(systems.items()):
    xs = [s + (k - (len(systems) - 1) / 2) * 0.25 for s in SIZES]
    rate = [100 * d[s][0] / d[s][1] for s in SIZES]
    lo = [100 * wilson(*d[s])[0] for s in SIZES]
    hi = [100 * wilson(*d[s])[1] for s in SIZES]
    ax.errorbar(xs, rate, yerr=[[r - l for r, l in zip(rate, lo)],
                                [h - r for r, h in zip(rate, hi)]],
                marker="o", capsize=3, label=name)
    for s, r, l, h in zip(SIZES, rate, lo, hi):
        rows.append({"system": name, "size": s, "k": d[s][0], "n": d[s][1],
                     "rate_pct": round(r, 1), "ci95_lo": round(l, 1), "ci95_hi": round(h, 1)})
ax.set_xticks(SIZES)
ax.set_xticklabels([f"{s}x{s}" for s in SIZES])
ax.set_ylim(-5, 105)
ax.set_xlabel("grid size")
ax.set_ylabel("legal AND optimal path (%)")
ax.set_title("Optimality vs size (n=10 per size, bars = Wilson 95% CI)")
ax.legend(fontsize=8, loc="center right")
fig.tight_layout()
FIG.mkdir(exist_ok=True)
fig.savefig(FIG / "scaling.png", dpi=150)
out = pd.DataFrame(rows)
out.to_csv(RES / "scaling_summary.csv", index=False)
print(out.to_string(index=False))
print("\nsaved fig/scaling.png")
