"""Analysis 4: effective branching factor b* of A* for each heuristic.
b* is the branching factor of a UNIFORM tree of depth d that would contain N nodes:
        N + 1 = 1 + b* + b*^2 + ... + b*^d
Convention (same as the course notebook): N = node EXPANSIONS of the A* run,
d = solution length (steps).  Solved numerically by bisection.
Reads ../results/*.csv. Writes ../results/analysis4_bstar.csv (per instance) and
../results/analysis4_summary.csv (median/IQR per level).  Run: python3 analysis4.py"""
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
RES = HERE.parent / "results"


def effective_bf(N, d, tol=1e-9):
    """Solve N + 1 = sum_{i=0..d} b^i for b by bisection (b >= 1)."""
    def total(b):
        return sum(b ** i for i in range(d + 1))
    assert N >= d, "A* must expand at least d nodes"
    lo, hi = 1.0, 20.0
    while hi - lo > tol:
        mid = (lo + hi) / 2
        if total(mid) < N + 1:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


# sanity check against a case with a known answer: a perfect binary tree of depth 3
# has 1+2+4+8 = 15 nodes -> N = 14 -> b* must be 2
assert abs(effective_bf(14, 3) - 2.0) < 1e-6

frames = []
for dom, f, algos in (("8puzzle", "classical_8puzzle.csv",
                       ["astar_misplaced", "astar_manhattan"]),
                      ("grid", "classical_grid.csv", ["astar_manhattan"])):
    d = pd.read_csv(RES / f)
    d = d[d.algo.isin(algos) & (d.status == "ok")].copy()
    d["bstar"] = [effective_bf(int(n), int(l))
                  for n, l in zip(d.expansions, d.length)]
    frames.append(d[["domain", "level", "instance", "algo", "length",
                     "expansions", "bstar"]])
per_inst = pd.concat(frames)
per_inst.to_csv(RES / "analysis4_bstar.csv", index=False)


def q1(x): return x.quantile(0.25)
def q3(x): return x.quantile(0.75)


summary = (per_inst.groupby(["domain", "algo", "level"])["bstar"]
           .agg(n="count", median="median", q1=q1, q3=q3).round(3).reset_index())
summary.to_csv(RES / "analysis4_summary.csv", index=False)
print(summary.to_string(index=False))

# dominance consequence: b*(manhattan) <= b*(misplaced) per 8-puzzle instance
w = per_inst[per_inst.domain == "8puzzle"].pivot_table(
    index=["level", "instance"], columns="algo", values="bstar")
print(f"\n8-puzzle instances with b*(Manhattan) > b*(misplaced): "
      f"{int((w['astar_manhattan'] > w['astar_misplaced']).sum())} of {len(w)}")
