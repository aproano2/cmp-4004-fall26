"""Part 2 — the duel instances and the reference solver, built on Part 1's code.

Nothing here re-implements search: the optimal costs and the A* tool come from
the group's Part-1 code (`algorithms.astar_puzzle` + `h_manhattan`, and
`gridworld.astar` + `grid_h_manhattan_scaled`), on the SAME instance banks
(`instances_8puzzle.json`, `instances_grid.json`) used in Part 1.

Conventions shown to the model (and checked by `validator.py`):

8-puzzle
    State: 9 numbers row by row, 0 = blank. Goal (1,2,3,4,5,6,7,8,0).
    A move letter says where the BLANK goes: U, D, L, R. Every move costs 1.
    (Part 1's EightPuzzle uses the index the blank moves to; `index_moves_to_letters`
    converts between the two.)

Weighted grid (Week-4 gridworld, no walls)
    '.' road = 1, ',' grass = 3, '~' water = 8, 'S' start, 'G' goal = 1.
    Cost is paid on ENTERING a cell; the start cell is not paid.
    Coordinates (row, col), 0-indexed, row 0 at the top; 4-connected moves.
"""
import json
from pathlib import Path

from algorithms import astar_puzzle, grid_h_manhattan_scaled, h_manhattan
from gridworld import TERRAIN, GridProblem
from gridworld import astar as grid_astar
from search import GOAL, EightPuzzle

CODE_DIR = Path(__file__).resolve().parent
PUZZLE_FILE = CODE_DIR / "instances_8puzzle.json"
GRID_FILE = CODE_DIR / "instances_grid.json"

LEVELS = {"8puzzle": [4, 8, 12, 16], "grid": [5, 8, 12, 16]}
MOVE_DELTA = {"U": (-1, 0), "D": (1, 0), "L": (0, -1), "R": (0, 1)}


# --------------------------------------------------------------- 8-puzzle
def step8(state, move):
    """Move the blank one cell. Returns the new tuple, or None if it leaves the board."""
    b = state.index(0)
    r, c = divmod(b, 3)
    dr, dc = MOVE_DELTA[move]
    nr, nc = r + dr, c + dc
    if not (0 <= nr < 3 and 0 <= nc < 3):
        return None
    s = list(state)
    nb = nr * 3 + nc
    s[b], s[nb] = s[nb], s[b]
    return tuple(s)


def index_moves_to_letters(start, index_moves):
    """Part-1 EightPuzzle actions (target index of the blank) -> 'UDLR' string."""
    letters, b = [], tuple(start).index(0)
    for a in index_moves:
        letters.append({-3: "U", 3: "D", -1: "L", 1: "R"}[a - b])
        b = a
    return "".join(letters)


def solvable8(state):
    tiles = [t for t in state if t != 0]
    inv = sum(1 for i in range(8) for j in range(i + 1, 8) if tiles[i] > tiles[j])
    return inv % 2 == 0


def solve_8puzzle(start):
    """Part-1 A* with Manhattan. -> (moves 'UDLR', cost, expansions)."""
    node, expansions = astar_puzzle(EightPuzzle(tuple(start)), h_manhattan)
    if node is None:
        return None
    return index_moves_to_letters(start, node.path()), node.g, expansions


# -------------------------------------------------------------------- grid
def find_cell(rows, ch):
    for r, row in enumerate(rows):
        c = row.find(ch)
        if c != -1:
            return (r, c)
    return None


def cell_cost(ch):
    return TERRAIN[ch]


def check_grid(rows):
    """Raise ValueError if `rows` is not a valid gridworld grid (used by the tool)."""
    if not isinstance(rows, list) or not rows or not all(isinstance(x, str) for x in rows):
        raise ValueError("`grid` must be a non-empty list of strings")
    if any(len(x) != len(rows[0]) for x in rows):
        raise ValueError("grid rows have different lengths")
    bad = {ch for x in rows for ch in x} - set(TERRAIN)
    if bad:
        raise ValueError(f"invalid characters in grid: {sorted(bad)}; use only . , ~ S G")
    if sum(x.count("S") for x in rows) != 1 or sum(x.count("G") for x in rows) != 1:
        raise ValueError("grid needs exactly one S and one G")


def solve_grid(rows):
    """Part-1 (Week-4) A* with Manhattan x MIN_COST. -> (cells [(r,c)...], cost, expansions)."""
    problem = GridProblem(rows)
    node, expansions = grid_astar(problem, grid_h_manhattan_scaled)
    if node is None:
        return None
    cells = [problem.initial]
    for m in node.path():
        cells.append(problem.result(cells[-1], m))
    return cells, node.g, expansions


# --------------------------------------------------------------- instances
def build_instances():
    """All 80 instances as dicts, in Part-1 order. `instance_id` is 1..10, as in
    results/classical_results.csv, so rows can be joined across Part 1 and 2."""
    out = []
    puzzles = json.loads(PUZZLE_FILE.read_text(encoding="utf-8"))["instances"]
    for level in LEVELS["8puzzle"]:
        for i, state in enumerate(puzzles[str(level)], start=1):
            moves, cost, _ = solve_8puzzle(state)
            out.append({"key": f"8puzzle-{level}-{i:02d}", "domain": "8puzzle", "level": level,
                        "instance_id": i, "start": list(state), "optimal_cost": cost,
                        "optimal_path": moves})
    grids = json.loads(GRID_FILE.read_text(encoding="utf-8"))["instances"]
    for level in LEVELS["grid"]:
        for i, rows in enumerate(grids[str(level)], start=1):
            cells, cost, _ = solve_grid(rows)
            out.append({"key": f"grid-{level}-{i:02d}", "domain": "grid", "level": level,
                        "instance_id": i, "rows": rows, "optimal_cost": cost,
                        "optimal_path": [list(c) for c in cells]})
    return out


def select(instances, domains=None, levels=None, n_per_level=None):
    keep = []
    for inst in instances:
        if domains and inst["domain"] not in domains:
            continue
        if levels and inst["level"] not in levels:
            continue
        if n_per_level and inst["instance_id"] > n_per_level:
            continue
        keep.append(inst)
    return keep


def get(instances, domain, level, instance_id):
    for inst in instances:
        if (inst["domain"], inst["level"], inst["instance_id"]) == (domain, level, instance_id):
            return inst
    raise KeyError((domain, level, instance_id))


assert GOAL == (1, 2, 3, 4, 5, 6, 7, 8, 0)
