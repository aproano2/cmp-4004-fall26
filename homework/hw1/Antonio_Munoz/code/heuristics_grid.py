"""Week 4 studio — REFERENCE SOLUTION (instructor-only).

A filled-in copy of ``starter.py``: identical function names and signatures, so
the *provided* ``test_heuristics.py`` passes when this module is imported in place
of ``starter``. Verify with ``studios/_verify_solutions.py`` (which aliases this
file to the name ``starter`` and runs the unmodified test).

DO NOT ship this to students — it is excluded via ``studios/.gitignore``. The
teaching walkthrough lives in ``solution.ipynb`` (which imports this file rather
than re-pasting it, so the two never drift).
"""
from math import hypot

from gridworld import GridProblem, astar, MIN_COST, MAX_COST


# ---- Task 1: implement four heuristics --------------------------------------

def h_zero(problem: GridProblem, state) -> int:
    """Admissible, useless. A* degenerates to uniform-cost search."""
    return 0


def h_manhattan(problem: GridProblem, state) -> int:
    """Plain Manhattan distance to the goal.

    On this grid *this happens to be admissible* because ``MIN_COST == 1`` — the
    cheapest possible step cost is exactly 1, so |dr|+|dc| can never exceed the
    true remaining cost. If ``MIN_COST`` were 2, this would UNDERcount by up to a
    factor of 2 (so still admissible, but strictly *dominated* by the scaled
    version below, which would then be the tighter admissible bound).
    """
    gr, gc = problem.goal
    r, c = state
    return abs(r - gr) + abs(c - gc)


def h_manhattan_scaled(problem: GridProblem, state) -> int:
    """Manhattan distance × MIN_COST — the correct admissible heuristic for a
    weighted grid where every step costs at least MIN_COST."""
    gr, gc = problem.goal
    r, c = state
    return (abs(r - gr) + abs(c - gc)) * MIN_COST


def h_euclidean_scaled(problem: GridProblem, state) -> float:
    """Euclidean distance × MIN_COST. On a 4-connected grid this is admissible
    but *weaker* than the scaled Manhattan (Euclidean <= Manhattan)."""
    gr, gc = problem.goal
    r, c = state
    return hypot(r - gr, c - gc) * MIN_COST


def h_bad(problem: GridProblem, state) -> int:
    """INADMISSIBLE — overestimates wherever the optimal path runs through cheap
    cells. Form: ``MAX_COST × Manhattan``. Since MAX_COST = 8 but a good path
    usually takes '.' (cost 1) cells, this assumes every step is the most
    expensive terrain and so overshoots the true remaining cost. A* with an
    inadmissible heuristic can (and here does) return a suboptimal path."""
    gr, gc = problem.goal
    r, c = state
    return (abs(r - gr) + abs(c - gc)) * MAX_COST


# ---- Task 2 sketch (the LLM duel) -------------------------------------------
# See README.md §"Task 2". Prompts and instance rendering live in duel.py,
# which imports ``gridworld.render`` and pulls its grids from ``instances.json``.
# You do NOT need to write duel.py — it's provided; you supply the model call
# via aicourse.llm and record the failure-category counts.


if __name__ == "__main__":
    from gridworld import load_instances
    grid = load_instances()[5][0]
    print("\n".join(grid), "\n")
    prob = GridProblem(grid)
    for name, h in [("zero", h_zero), ("manhattan", h_manhattan),
                    ("manhattan_scaled", h_manhattan_scaled),
                    ("euclidean_scaled", h_euclidean_scaled),
                    ("bad", h_bad)]:
        node, exp = astar(prob, h)
        cost = node.g if node else None
        print(f"  {name:<20} cost={cost}  expansions={exp}")
