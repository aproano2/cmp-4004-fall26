"""Analysis 1: (a) UCS and A*(admissible h) return equal-cost solutions;
(b) BFS is NOT optimal on non-uniform costs. Reads ../results/*.csv.
Writes ../results/analysis1_summary.csv and ../fig/bfs_vs_ucs.png.
Run: python3 analysis1.py"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

import gridworld as GW

HERE = Path(__file__).parent
RES, FIG = HERE.parent / "results", HERE.parent / "fig"
FIG.mkdir(exist_ok=True)

p8 = pd.read_csv(RES / "classical_8puzzle.csv")
gr = pd.read_csv(RES / "classical_grid.csv")


def wide(df):
    """One row per instance, one cost column per algorithm."""
    return df.pivot_table(index=["level", "instance"], columns="algo",
                          values="cost", aggfunc="first")


w8, wg = wide(p8), wide(gr)
rows = []

# (a) UCS == A* (admissible h), every instance
for dom, w, a_names in (("8puzzle", w8, ["astar_manhattan", "astar_misplaced"]),
                        ("grid", wg, ["astar_manhattan"])):
    for a in a_names:
        for level, sub in w.groupby(level="level"):
            eq = int((sub["ucs"] == sub[a]).sum())
            rows.append({"check": f"UCS == {a}", "domain": dom, "level": level,
                         "n": len(sub), "matches": eq, "median_ratio": 1.0})
        assert (w["ucs"] == w[a]).all(), f"UCS != {a} somewhere in {dom}!"

# (b) BFS vs UCS
for dom, w in (("8puzzle", w8), ("grid", wg)):
    for level, sub in w.groupby(level="level"):
        sub_ok = sub.dropna(subset=["bfs", "ucs"])
        worse = int((sub_ok["bfs"] > sub_ok["ucs"]).sum())
        ratio = (sub_ok["bfs"] / sub_ok["ucs"]).median()
        rows.append({"check": "BFS suboptimal (cost > UCS)", "domain": dom,
                     "level": level, "n": len(sub_ok), "matches": worse,
                     "median_ratio": round(float(ratio), 3)})
summary = pd.DataFrame(rows)
summary.to_csv(RES / "analysis1_summary.csv", index=False)
print(summary.to_string(index=False))

# pick the showcase instance: biggest BFS/UCS cost ratio on a SMALL grid (readable)
cand = wg.reset_index()
cand = cand[cand["level"] <= 8].copy()
cand["ratio"] = cand["bfs"] / cand["ucs"]
best = cand.sort_values("ratio", ascending=False).iloc[0]
lvl, idx = int(best["level"]), int(best["instance"])
print(f"\nShowcase: grid {lvl}x{lvl}, instance {idx}: BFS cost {int(best['bfs'])} "
      f"vs UCS cost {int(best['ucs'])}")

grid = GW.load_instances(HERE / "instances_grid.json")[lvl][idx]
prob = GW.GridProblem(grid)
shade = {".": 0.92, ",": 0.65, "~": 0.35, "S": 0.92, "G": 0.92}
fig, axes = plt.subplots(1, 2, figsize=(9, 4.6))
for ax, algo in zip(axes, ["bfs", "ucs"]):
    row = gr[(gr.level == lvl) & (gr.instance == idx) & (gr.algo == algo)].iloc[0]
    ax.imshow([[shade[c] for c in r] for r in grid], cmap="gray", vmin=0, vmax=1)
    pos, (r, c) = [prob.initial], prob.initial
    for m in row["path"].split(","):
        dr, dc = GW.MOVES[m]
        r, c = r + dr, c + dc
        pos.append((r, c))
    ax.plot([p[1] for p in pos], [p[0] for p in pos], "r-o", ms=4, lw=2)
    for i, rr in enumerate(grid):
        for j, ch in enumerate(rr):
            ax.text(j, i, ch if ch in "SG" else {".": "1", ",": "3", "~": "8"}[ch],
                    ha="center", va="center", fontsize=7,
                    color="blue" if ch in "SG" else "black")
    ax.set_title(f"{algo.upper()}: {int(row['length'])} steps, cost {int(row['cost'])}")
    ax.set_xticks([]); ax.set_yticks([])
fig.suptitle(f"Grid {lvl}x{lvl}, instance {idx}: fewest steps (BFS) is not cheapest (UCS)")
fig.tight_layout()
fig.savefig(FIG / "bfs_vs_ucs.png", dpi=150)
print("saved fig/bfs_vs_ucs.png")
