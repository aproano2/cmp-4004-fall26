"""Analysis 2: heuristic dominance. Manhattan (h2) must expand no more nodes than
misplaced-tiles (h1) on every instance.  Two levels of evidence:
  (a) STATE level: h2(s) >= h1(s), and both <= true distance, on ALL 181,440
      reachable 8-puzzle states (this is WHY dominance holds);
  (b) INSTANCE level: expansions(h2) <= expansions(h1) on each of the 40 instances.
Reads ../results/classical_8puzzle.csv. Writes ../results/analysis2_summary.csv
and ../fig/dominance.png.   Run: python3 analysis2.py"""
from collections import deque
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

import heuristics_8p as H
import search as S

HERE = Path(__file__).parent
RES, FIG = HERE.parent / "results", HERE.parent / "fig"
FIG.mkdir(exist_ok=True)

# ---- (a) all reachable states: true distance by BFS from the goal ----------
puz = S.EightPuzzle(S.GOAL)
dist = {S.GOAL: 0}
q = deque([S.GOAL])
while q:
    s = q.popleft()
    for a in puz.actions(s):
        t = puz.result(s, a)
        if t not in dist:
            dist[t] = dist[s] + 1
            q.append(t)
dom_viol = adm1_viol = adm2_viol = 0
for s, d in dist.items():
    h1, h2 = H.h_misplaced(puz, s), H.h_manhattan(puz, s)
    dom_viol += h2 < h1
    adm1_viol += h1 > d
    adm2_viol += h2 > d
print(f"States checked: {len(dist):,}")
print(f"  h2 < h1 (dominance violated): {dom_viol}")
print(f"  h1 > true distance (misplaced inadmissible): {adm1_viol}")
print(f"  h2 > true distance (manhattan inadmissible): {adm2_viol}")

# ---- (b) per-instance expansions -------------------------------------------
d = pd.read_csv(RES / "classical_8puzzle.csv")
w = d.pivot_table(index=["level", "instance"], columns="algo", values="expansions")
viol = w[w["astar_manhattan"] > w["astar_misplaced"]]
print(f"\nInstances where Manhattan expands MORE than misplaced: {len(viol)} of {len(w)}")


def q1(x): return x.quantile(0.25)
def q3(x): return x.quantile(0.75)


rows = []
for level, sub in w.groupby(level="level"):
    for a in ("astar_misplaced", "astar_manhattan"):
        x = sub[a]
        rows.append({"level": level, "algo": a, "median": x.median(),
                     "q1": q1(x), "q3": q3(x), "iqr": q3(x) - q1(x)})
    rows.append({"level": level, "algo": "violations (h2 > h1)",
                 "median": int((sub["astar_manhattan"] > sub["astar_misplaced"]).sum()),
                 "q1": None, "q3": None, "iqr": None})
summary = pd.DataFrame(rows)
summary.to_csv(RES / "analysis2_summary.csv", index=False)
print("\n" + summary.to_string(index=False))

# ---- figure: expansions vs depth, log y, median with IQR bars --------------
fig, ax = plt.subplots(figsize=(6, 4))
for a, lab, off in (("astar_misplaced", "A* + misplaced tiles", -0.15),
                    ("astar_manhattan", "A* + Manhattan", 0.15)):
    s = summary[summary.algo == a]
    xs = [lv + off for lv in s.level]
    ax.errorbar(xs, s["median"], yerr=[s["median"] - s["q1"], s["q3"] - s["median"]],
                marker="o", capsize=3, label=lab)
ax.set_yscale("log")
ax.set_xticks([4, 8, 12, 16])
ax.set_xlabel("optimal solution depth")
ax.set_ylabel("node expansions (median, IQR bars)")
ax.set_title("Manhattan dominates misplaced tiles (n=10 per depth)")
ax.legend()
fig.tight_layout()
fig.savefig(FIG / "dominance.png", dpi=150)
print("\nsaved fig/dominance.png")
