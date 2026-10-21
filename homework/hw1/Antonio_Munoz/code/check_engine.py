"""Proves engine.py is faithful: on every instance its expansions and costs must
equal the course's search()/astar()/ids(). Run: python3 check_engine.py"""
import algorithms as A
import engine
import gridworld as GW
import heuristics_8p as H8
import heuristics_grid as HG
import search as S

bank8 = S.load_instances("instances_8puzzle.json")
bankg = GW.load_instances("instances_grid.json")
bad = 0


def same(label, ref_node, ref_exp, r):
    global bad
    ok = (r["status"] == "ok" and r["expansions"] == ref_exp
          and r["cost"] == ref_node.g)
    if not ok:
        bad += 1
        print("MISMATCH", label, "ref:", ref_node.g, ref_exp,
              "engine:", r["cost"], r["expansions"], r["status"])


n = 0
for depth, states in bank8.items():
    for st in states:
        p = S.EightPuzzle(st)
        for name in ("bfs", "dfs", "ucs", "ids"):
            node, exp = getattr(A, name)(p)
            same(f"8p d{depth} {name}", node, exp,
                 engine.run(p, name, timeout=120))
            n += 1
        for hn, h in (("misplaced", H8.h_misplaced), ("manhattan", H8.h_manhattan)):
            node, exp = GW.astar(p, h)
            same(f"8p d{depth} astar-{hn}", node, exp,
                 engine.run(p, "astar", h, timeout=120))
            n += 1
for size, grids in bankg.items():
    for g in grids:
        p = GW.GridProblem(g)
        for name in ("bfs", "dfs", "ucs"):
            node, exp = getattr(A, name)(p)
            same(f"grid {size} {name}", node, exp,
                 engine.run(p, name, timeout=120))
            n += 1
        node, exp = GW.astar(p, HG.h_manhattan_scaled)
        same(f"grid {size} astar", node, exp,
             engine.run(p, "astar", HG.h_manhattan_scaled, timeout=120))
        n += 1
print(f"{n} comparisons, {bad} mismatches")
