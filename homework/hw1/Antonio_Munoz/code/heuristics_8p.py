"""8-puzzle heuristics with the engine's signature h(problem, state).
Neither counts the blank (counting it breaks admissibility)."""
from search import GOAL

_POS = {t: divmod(i, 3) for i, t in enumerate(GOAL)}


def h_misplaced(problem, state):
    return sum(1 for i, v in enumerate(state) if v != 0 and v != GOAL[i])


def h_manhattan(problem, state):
    total = 0
    for i, v in enumerate(state):
        if v != 0:
            r, c = divmod(i, 3)
            gr, gc = _POS[v]
            total += abs(r - gr) + abs(c - gc)
    return total


def scaled(h, w):
    """w * h. With w=3 this breaks admissibility on purpose (analysis 3)."""
    return lambda problem, state: w * h(problem, state)
