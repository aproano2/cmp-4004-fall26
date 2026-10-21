"""Duel 1 / Part 2 — the validator. It never asks a model anything.

Every answer, from every system (A*, the bare LLM, the tool-augmented LLM), goes
through the same three checks, in this order:

  1. Is the path LEGAL?   non-empty, starts on S, ends on G, every cell in
                          bounds, no wall cells, every step 4-adjacent.
  2. Is it OPTIMAL?       its true cost (recomputed here from the terrain)
                          equals the cost A*+manhattan finds (admissible, so
                          that cost is the optimum).
  3. Is the REPORTED cost right?  the number the system wrote down equals the
                          true cost recomputed in step 1.

Categories (counted separately, as the spec requires):

    malformed    no path could be parsed from the output at all
    illegal      failure category 1 — the path breaks a rule of the grid
    suboptimal   failure category 2 — legal, but costs more than A*
    wrong_cost   failure category 3 — legal and optimal, reported cost wrong
    optimal      legal, optimal, and the reported cost is right

A suboptimal path whose reported cost is *also* wrong is counted as
``suboptimal`` (the worse failure); ``cost_ok`` records the cost check
independently so nothing is lost.

The cost model is gridworld's: the cost of a path is the sum of the costs of
the cells *entered* (the start cell is not charged), with '.'=1 ','=3 '~'=8,
'G'=1.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from engine import search as _search
from gridworld import TERRAIN, GridProblem
from starter import h_manhattan

WALL = "#"          # the course banks contain no walls; checked anyway

MALFORMED = "malformed"
ILLEGAL = "illegal"
SUBOPTIMAL = "suboptimal"
WRONG_COST = "wrong_cost"
OPTIMAL = "optimal"
CATEGORIES = (OPTIMAL, WRONG_COST, SUBOPTIMAL, ILLEGAL, MALFORMED)


@dataclass
class Verdict:
    category: str
    legal: bool = False
    true_cost: float | None = None
    reported_cost: float | None = None
    optimal_cost: float | None = None
    cost_ok: bool = False
    reasons: list[str] = field(default_factory=list)

    @property
    def correct(self) -> bool:
        return self.category == OPTIMAL


def optimal_cost(grid) -> int:
    """The reference optimum: A* with Manhattan (admissible because the
    cheapest terrain costs 1). Part 1 checked it equals UCS on all 40 grids."""
    r = _search(GridProblem(grid), "astar", h=h_manhattan)
    if not r.solved:
        raise RuntimeError("reference A* failed to solve a bank instance")
    return r.cost


def find(grid, ch):
    for r, row in enumerate(grid):
        c = row.find(ch)
        if c != -1:
            return (r, c)
    raise ValueError(f"grid has no {ch!r}")


def check_path(grid, path) -> tuple[bool, float | None, list[str]]:
    """Legality + true cost. Returns (legal, true_cost, reasons)."""
    reasons: list[str] = []
    if not path:
        return False, None, ["empty path"]
    rows, cols = len(grid), len(grid[0])
    cells = []
    for i, cell in enumerate(path):
        try:
            r, c = int(cell[0]), int(cell[1])
            if len(cell) != 2:
                raise ValueError
        except (TypeError, ValueError, IndexError):
            return False, None, [f"step {i}: {cell!r} is not a [row, col] pair"]
        cells.append((r, c))

    if cells[0] != find(grid, "S"):
        reasons.append(f"starts at {list(cells[0])}, S is at {list(find(grid, 'S'))}")
    if cells[-1] != find(grid, "G"):
        reasons.append(f"ends at {list(cells[-1])}, G is at {list(find(grid, 'G'))}")
    cost = 0
    for i, (r, c) in enumerate(cells):
        if not (0 <= r < rows and 0 <= c < cols):
            reasons.append(f"step {i}: {[r, c]} is out of bounds")
            continue
        if grid[r][c] == WALL:
            reasons.append(f"step {i}: {[r, c]} is a wall")
        if i > 0:
            pr, pc = cells[i - 1]
            if abs(r - pr) + abs(c - pc) != 1:
                reasons.append(f"step {i}: {[pr, pc]} -> {[r, c]} is not a single "
                               f"up/down/left/right move")
            cost += TERRAIN.get(grid[r][c], 0)
    legal = not reasons
    return legal, (cost if legal else None), reasons


def validate(grid, path, reported_cost, opt: float | None = None) -> Verdict:
    """The single entry point. ``path`` is a list of [row, col] (or None when
    nothing could be parsed); ``reported_cost`` is whatever the system claimed."""
    opt = optimal_cost(grid) if opt is None else opt
    rep = _as_number(reported_cost)
    if path is None:
        return Verdict(MALFORMED, reported_cost=rep, optimal_cost=opt,
                       reasons=["no parseable path"])
    legal, true_cost, reasons = check_path(grid, path)
    v = Verdict(ILLEGAL, legal=legal, true_cost=true_cost, reported_cost=rep,
                optimal_cost=opt, reasons=reasons)
    if not legal:
        return v
    v.cost_ok = rep is not None and abs(rep - true_cost) < 1e-9
    if true_cost > opt:
        v.category = SUBOPTIMAL
        v.reasons.append(f"true cost {true_cost} > optimal {opt}")
    elif not v.cost_ok:
        v.category = WRONG_COST
        v.reasons.append(f"reported cost {reported_cost!r} != true cost {true_cost}")
    else:
        v.category = OPTIMAL
    if true_cost < opt:                       # would mean A* is wrong — loud
        raise AssertionError(f"legal path cheaper than A* ({true_cost} < {opt})")
    return v


def _as_number(x):
    if isinstance(x, bool):
        return None
    if isinstance(x, (int, float)):
        return float(x)
    if isinstance(x, str):
        m = re.fullmatch(r"\s*(-?\d+(?:\.\d+)?)\s*", x)
        return float(m.group(1)) if m else None
    return None


# ---------------------------------------------------------------------------
# The 8-puzzle — the same five categories, checked the same way.
#
# An answer is a list of moves of the BLANK: 'U', 'D', 'L', 'R' (words such as
# "up" are accepted). Every move costs 1, so the true cost is the number of
# moves. LEGAL means every move keeps the blank on the board AND the sequence
# ends on the goal state; OPTIMAL means its length equals A*+Manhattan's.
# ---------------------------------------------------------------------------
PUZZLE_GOAL = (1, 2, 3, 4, 5, 6, 7, 8, 0)
BLANK_STEP = {"U": -3, "D": 3, "L": -1, "R": 1}
_MOVE_WORDS = {"up": "U", "down": "D", "left": "L", "right": "R"}


def puzzle_optimal_cost(state) -> int:
    """Reference optimum for the 8-puzzle: A* with Manhattan (admissible)."""
    from search import EightPuzzle
    r = _search(EightPuzzle(tuple(state)), "astar", h=h_manhattan)
    if not r.solved:
        raise RuntimeError("reference A* failed to solve a bank instance")
    return r.cost


def normalize_move(m):
    if not isinstance(m, str):
        return None
    m = m.strip()
    if m.upper() in BLANK_STEP:
        return m.upper()
    return _MOVE_WORDS.get(m.lower())


def apply_moves(state, moves) -> tuple[tuple | None, list[str]]:
    """Play ``moves`` from ``state``. Returns (final state or None, reasons)."""
    s = list(state)
    for i, raw in enumerate(moves):
        m = normalize_move(raw)
        if m is None:
            return None, [f"move {i}: {raw!r} is not one of U/D/L/R"]
        b = s.index(0)
        if (m == "U" and b < 3) or (m == "D" and b > 5) \
                or (m == "L" and b % 3 == 0) or (m == "R" and b % 3 == 2):
            return None, [f"move {i}: {m} takes the blank off the board "
                          f"(blank at row {b // 3}, col {b % 3})"]
        t = b + BLANK_STEP[m]
        s[b], s[t] = s[t], s[b]
    return tuple(s), []


def validate_puzzle(state, moves, reported_cost, opt: int | None = None) -> Verdict:
    """Puzzle twin of ``validate``. ``moves`` is None when nothing parsed."""
    opt = puzzle_optimal_cost(state) if opt is None else opt
    rep = _as_number(reported_cost)
    if moves is None:
        return Verdict(MALFORMED, reported_cost=rep, optimal_cost=opt,
                       reasons=["no parseable move list"])
    if isinstance(moves, str):                 # "ULDR" is accepted as 4 moves
        moves = list(moves.replace(",", "").replace(" ", ""))
    if not isinstance(moves, list):
        return Verdict(ILLEGAL, reported_cost=rep, optimal_cost=opt,
                       reasons=[f"moves is a {type(moves).__name__}, not a list"])
    final, reasons = apply_moves(state, moves)
    if final is not None and final != PUZZLE_GOAL:
        reasons.append(f"ends on {list(final)}, not the goal {list(PUZZLE_GOAL)}")
    v = Verdict(ILLEGAL, optimal_cost=opt, reported_cost=rep, reasons=reasons)
    if reasons:
        return v
    n = len(moves)
    v.legal, v.true_cost = True, n
    v.cost_ok = rep is not None and abs(rep - n) < 1e-9
    if n > opt:
        v.category = SUBOPTIMAL
        v.reasons.append(f"{n} moves > optimal {opt}")
    elif not v.cost_ok:
        v.category = WRONG_COST
        v.reasons.append(f"reported cost {reported_cost!r} != true cost {n}")
    else:
        v.category = OPTIMAL
    if n < opt:
        raise AssertionError(f"legal solution shorter than A* ({n} < {opt})")
    return v
