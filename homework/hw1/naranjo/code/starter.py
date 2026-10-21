"""Duel 1 / Part 1 — our implementations: the five algorithms + the heuristics.

Names and signatures deliberately match the week-3 / week-4 studios so that the
*provided* tests copied into this folder run **unmodified**:

    test_search.py      -> s.bfs / s.dfs / s.ucs / s.ids, unpacked as (node, expansions)
    test_heuristics.py  -> s.h_zero / s.h_manhattan / s.h_manhattan_scaled /
                           s.h_euclidean_scaled / s.h_bad, each (problem, state)

Everything is a thin layer over ``engine.py``, which is where the measurement
(frontier size, deadline) lives. ``engine.search`` returns a ``Result`` that
unpacks as ``(node, expansions)``, so the studio interface still holds.

Two domains share one heuristic signature ``(problem, state) -> number``:
``h_manhattan`` and friends dispatch on the problem type, which is the only
clean way to tell a 9-tuple 8-puzzle state from a (row, col) grid state.
"""

from __future__ import annotations

from math import hypot

from engine import Result, depth_limited, ids as _ids, search as _search
from gridworld import MAX_COST, MIN_COST, GridProblem

# ---- the five algorithms ----------------------------------------------------


def bfs(problem) -> Result:
    """Breadth-first search. Complete; optimal only when step costs are uniform
    (true on the 8-puzzle, false on the weighted grid — analysis 1)."""
    return _search(problem, "fifo")


def dfs(problem) -> Result:
    """Depth-first (graph) search. The explored set is what makes it terminate
    on cyclic graphs. Complete on a finite space, never optimal."""
    return _search(problem, "lifo")


def ucs(problem) -> Result:
    """Uniform-cost search. Optimal for any non-negative step costs."""
    return _search(problem, "ucs")


def astar(problem, h) -> Result:
    """A* with heuristic ``h``. Optimal whenever ``h`` is admissible — and only
    then (see ``h_manhattan_x3`` / ``h_bad`` for the failure on demand)."""
    return _search(problem, "astar", h=h)


def ids(problem, timeout=None) -> Result:
    """Iterative deepening: BFS's completeness at O(bd) memory."""
    return _ids(problem, timeout=timeout)


# ---- heuristics: (problem, state) -> number ---------------------------------


def h_zero(problem, state) -> int:
    """Admissible, useless. A* with h = 0 is uniform-cost search — the reference
    point for "what does a heuristic actually buy", and the studio's baseline."""
    return 0


def h_misplaced(problem, state) -> int:
    """8-puzzle: count the tiles that are not on their goal square.

    Admissible because every misplaced tile needs at least one move to get
    there — and it counts *one* move per tile even when a tile can never move
    directly to its home square. This is the relaxation "a tile can move
    anywhere, instantly".
    """
    goal = problem.goal
    return sum(1 for i, v in enumerate(state) if v != 0 and v != goal[i])


def _manhattan_puzzle(state, goal) -> int:
    """Sum of per-tile Manhattan distances on the flat 3x3 state."""
    total = 0
    for i, v in enumerate(state):
        if v == 0:
            continue                      # the blank is not counted
        j = goal.index(v)
        total += abs(i // 3 - j // 3) + abs(i % 3 - j % 3)
    return total


def _manhattan_grid(state, goal) -> int:
    (r, c), (gr, gc) = state, goal
    return abs(r - gr) + abs(c - gc)


def h_manhattan(problem, state) -> int:
    """Manhattan distance to the goal, in both domains.

    8-puzzle: sum of per-tile Manhattan distances — admissible (a tile can only
    ever move to a neighbouring square) and it *dominates* ``h_misplaced``
    pointwise, since a misplaced tile is at distance >= 1.

    Grid: |dr| + |dc|. Admissible here because ``MIN_COST == 1`` — the cheapest
    possible step costs exactly as much as one Manhattan step. If ``MIN_COST``
    were 2 this would undercount, i.e. stay admissible but become dominated by
    ``h_manhattan_scaled``.
    """
    if isinstance(problem, GridProblem):
        return _manhattan_grid(state, problem.goal)
    return _manhattan_puzzle(state, problem.goal)


def h_manhattan_scaled(problem, state) -> int:
    """Manhattan x MIN_COST — the correct admissible heuristic for a weighted
    grid in general (provided by the studio test contract)."""
    return h_manhattan(problem, state) * MIN_COST


def h_euclidean_scaled(problem, state) -> float:
    """Euclidean x MIN_COST. Admissible on a 4-connected grid but strictly
    weaker than scaled Manhattan (Euclidean <= Manhattan)."""
    (r, c), (gr, gc) = state, problem.goal
    return hypot(r - gr, c - gc) * MIN_COST


def h_manhattan_x3(problem, state) -> int:
    """DELIBERATELY INADMISSIBLE: 3 x Manhattan on the 8-puzzle.

    It overestimates whenever the optimal path does not fan out — the classic
    weighted-A* trade. Analysis 3 reports both numbers: the expansion/time
    speedup *and* the solution-cost penalty. No optimality claim survives this.
    """
    return 3 * h_manhattan(problem, state)


def h_bad(problem, state) -> int:
    """DELIBERATELY INADMISSIBLE on the grid: MAX_COST x Manhattan = 8 x.

    It assumes every remaining step costs the most expensive terrain, while a
    good path usually runs through cheap road. The studio test asserts it
    breaks optimality on at least one of the 40 grids.
    """
    return h_manhattan(problem, state) * MAX_COST


# ---- a small shared driver used by the harness ------------------------------


def algorithms(domain: str):
    """The benchmark registry: ``(name, callable)`` pairs.

    Every callable has the signature ``fn(problem, timeout=None) -> Result`` so
    the harness can hand all seven the same hard deadline. ``domain`` is
    ``"puzzle"`` (8-puzzle, uniform cost) or ``"grid"`` (weighted terrain).
    IDS is included in both: it is one of the five algorithms Duel 1 measures.
    """
    if domain == "puzzle":
        return [
            ("BFS", lambda p, timeout=None: _search(p, "fifo", timeout=timeout)),
            ("DFS", lambda p, timeout=None: _search(p, "lifo", timeout=timeout)),
            ("UCS", lambda p, timeout=None: _search(p, "ucs", timeout=timeout)),
            ("IDS", lambda p, timeout=None: _ids(p, timeout=timeout)),
            ("A*+misplaced", lambda p, timeout=None: _search(p, "astar", h=h_misplaced, timeout=timeout)),
            ("A*+manhattan", lambda p, timeout=None: _search(p, "astar", h=h_manhattan, timeout=timeout)),
            ("A*+3xmanhattan", lambda p, timeout=None: _search(p, "astar", h=h_manhattan_x3, timeout=timeout)),
        ]
    if domain == "grid":
        return [
            ("BFS", lambda p, timeout=None: _search(p, "fifo", timeout=timeout)),
            ("DFS", lambda p, timeout=None: _search(p, "lifo", timeout=timeout)),
            ("UCS", lambda p, timeout=None: _search(p, "ucs", timeout=timeout)),
            ("IDS", lambda p, timeout=None: _ids(p, timeout=timeout)),
            ("A*+manhattan", lambda p, timeout=None: _search(p, "astar", h=h_manhattan, timeout=timeout)),
            ("A*+3xmanhattan", lambda p, timeout=None: _search(p, "astar", h=h_manhattan_x3, timeout=timeout)),
            ("A*+8xmanhattan", lambda p, timeout=None: _search(p, "astar", h=h_bad, timeout=timeout)),
        ]
    raise ValueError(domain)


if __name__ == "__main__":
    from search import D8, EightPuzzle

    p = EightPuzzle(D8)
    for name, algo in algorithms("puzzle"):
        r = algo(p)
        print(f"  {name:<16} status={r.status:<9} len={r.length} "
              f"cost={r.cost} expansions={r.expansions:,} max_frontier={r.max_frontier:,} "
              f"{r.seconds:.3f}s")
