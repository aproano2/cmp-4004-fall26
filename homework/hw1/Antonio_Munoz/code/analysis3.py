"""Analysis 3: break admissibility with h x 3 (weighted A*, w=3).
Reports BOTH numbers the assignment requires:
  speedup      = expansions(A*) / expansions(A* x3), and time ratio
  quality cost = cost(A* x3) / optimal cost, and % of instances that are suboptimal
Optimal cost = A* with the admissible heuristic (== UCS, shown in analysis 1).
Reads ../results/*.csv. Writes ../results/analysis3_summary.csv and
../fig/inadmissible_tradeoff.png.   Run: python3 analysis3.py"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).parent
RES, FIG = HERE.parent / "results", HERE.parent / "fig"
FIG.mkdir(exist_ok=True)

rows = []
for dom, f in (("8puzzle", "classical_8puzzle.csv"), ("grid", "classical_grid.csv")):
    d = pd.read_csv(RES / f)
    w = {v: d.pivot_table(index=["level", "instance"], columns="algo", values=v,
                          aggfunc="first")
         for v in ("cost", "expansions", "time_s")}
    t = pd.DataFrame({
        "exp_opt": w["expansions"]["astar_manhattan"],
        "exp_x3": w["expansions"]["astar_manhattan_x3"],
        "time_opt": w["time_s"]["astar_manhattan"],
        "time_x3": w["time_s"]["astar_manhattan_x3"],
        "cost_opt": w["cost"]["astar_manhattan"],
        "cost_x3": w["cost"]["astar_manhattan_x3"],
    })
    t["speedup_exp"] = t.exp_opt / t.exp_x3
    t["speedup_time"] = t.time_opt / t.time_x3
    t["cost_ratio"] = t.cost_x3 / t.cost_opt
    t["subopt"] = t.cost_x3 > t.cost_opt
    assert (t.cost_x3 >= t.cost_opt).all(), "x3 found a cheaper path than optimal: bug"
    assert (t.cost_ratio <= 3 + 1e-9).all(), "violates the w*C* bound: bug"
    for level, s in t.groupby(level="level"):
        rows.append({"domain": dom, "level": level, "n": len(s),
                     "median_exp_opt": s.exp_opt.median(),
                     "median_exp_x3": s.exp_x3.median(),
                     "median_speedup_exp": round(s.speedup_exp.median(), 2),
                     "median_speedup_time": round(s.speedup_time.median(), 2),
                     "n_suboptimal": int(s.subopt.sum()),
                     "median_cost_ratio": round(s.cost_ratio.median(), 3),
                     "max_cost_ratio": round(s.cost_ratio.max(), 3)})
summary = pd.DataFrame(rows)
summary.to_csv(RES / "analysis3_summary.csv", index=False)
print(summary.to_string(index=False))

# ---- figure: gain vs price, per level, both domains ------------------------
fig, axes = plt.subplots(1, 2, figsize=(9, 3.8))
for dom, mk in (("8puzzle", "o"), ("grid", "s")):
    s = summary[summary.domain == dom]
    axes[0].plot(s.level, s.median_speedup_exp, marker=mk, label=dom)
    axes[1].plot(s.level, s.n_suboptimal / s.n * 100, marker=mk, label=dom)
axes[0].axhline(1, color="gray", ls="--", lw=1)
axes[0].set_title("Gain: expansions saved (A* / A* x3)")
axes[0].set_ylabel("median speedup (x)")
axes[1].set_title("Price: instances with a worse path")
axes[1].set_ylabel("% suboptimal")
axes[1].set_ylim(0, 100)
for ax in axes:
    ax.set_xlabel("level (puzzle depth / grid size)")
    ax.legend()
fig.suptitle("h x 3 (inadmissible): gain depends on the domain, the price is real", y=1.0)
fig.tight_layout()
fig.savefig(FIG / "inadmissible_tradeoff.png", dpi=150)
print("\nsaved fig/inadmissible_tradeoff.png")
