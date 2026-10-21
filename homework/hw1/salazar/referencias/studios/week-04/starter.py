"""Week 4 studio — Task 1 starter (heuristics on a weighted grid).

Fill in the four heuristics below. Then run ``python3 test_heuristics.py``.
All required tests must pass, INCLUDING the failure test that asserts an
inadmissible heuristic breaks optimality — because a "guarantee" you cannot
watch fail is not a guarantee you understood.
"""
from gridworld import GridProblem, astar, MIN_COST, MAX_COST


# ---- Task 1: implement four heuristics --------------------------------------

def h_zero(problem: GridProblem, state) -> int:
    """Admissible, useless. A* degenerates to uniform-cost search."""
    return 0


def h_manhattan(problem: GridProblem, state) -> int:
    """Plain Manhattan distance to the goal.

    On this grid *this happens to be admissible* because MIN_COST == 1.
    Ask yourself: if MIN_COST were 2, would this still be admissible? Would it
    still be *dominated* by ``h_manhattan_scaled``?
    """
    # TODO: return |dr| + |dc| between state and problem.goal
    raise NotImplementedError


def h_manhattan_scaled(problem: GridProblem, state) -> int:
    """Manhattan distance × MIN_COST — the correct admissible heuristic for a
    weighted grid where every step costs at least MIN_COST."""
    # TODO
    raise NotImplementedError


def h_euclidean_scaled(problem: GridProblem, state) -> float:
    """Euclidean distance × MIN_COST. On a 4-connected grid this is admissible
    but *weaker* than the scaled Manhattan (Euclidean <= Manhattan)."""
    # TODO
    raise NotImplementedError


def h_bad(problem: GridProblem, state) -> int:
    """INADMISSIBLE — must overestimate at least somewhere.

    Suggested form: MAX_COST * Manhattan-distance. Since MAX_COST=8 but the
    optimal path often takes cheap cells, this happily overestimates.
    """
    # TODO
    raise NotImplementedError


# ---- Task 2 sketch (the LLM duel) -------------------------------------------
# See README.md §"Task 2". Prompts and instance rendering live in duel.py,
# which imports ``gridworld.render`` and pulls its grids from ``instances.json``.
# You do NOT need to write duel.py — it's provided; you supply the model call
# via aicourse.llm and record the failure-category counts.


if __name__ == "__main__":
    # Quick smoke test: solve one 5x5 instance with each heuristic you've filled in.
    from gridworld import load_instances
    grid = load_instances()[5][0]
    print("\n".join(grid), "\n")
    prob = GridProblem(grid)
    for name, h in [("zero", h_zero), ("manhattan", h_manhattan),
                    ("manhattan_scaled", h_manhattan_scaled),
                    ("euclidean_scaled", h_euclidean_scaled),
                    ("bad", h_bad)]:
        try:
            node, exp = astar(prob, h)
        except NotImplementedError:
            print(f"  {name:<20} not implemented yet")
            continue
        cost = node.g if node else None
        print(f"  {name:<20} cost={cost}  expansions={exp}")
