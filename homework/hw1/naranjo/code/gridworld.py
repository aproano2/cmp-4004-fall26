"""Week 4 studio — the shared search engine (GIVEN to you; do not modify).

This is the A* from the Session-A notebook, unchanged, plus a weighted-terrain
grid to run it on. Week 4 is about *heuristics*, not about re-implementing A* —
so the search is provided. You write the heuristics in ``starter.py``.

Terrain costs (the cost is charged on *entering* a cell):

    '.'  road   = 1
    ','  grass  = 3
    '~'  water  = 8
    'S'  start  (cost 1 to stand on)
    'G'  goal   (cost 1 to enter)

Interface (identical to week 3 / the notebook):
    problem.actions(state)        -> tuple of legal moves ('U'/'D'/'L'/'R')
    problem.result(state, action) -> next state
    problem.is_goal(state)        -> bool
    problem.step_cost(s, action)  -> cost of entering the destination cell
    astar(problem, h)             -> (goal_node, expansions)  or  (None, expansions)
    node.path()                   -> list of moves; node.g -> path cost
"""
import heapq
import json
from pathlib import Path

TERRAIN = {".": 1, ",": 3, "~": 8, "S": 1, "G": 1}
MOVES = {"U": (-1, 0), "D": (1, 0), "L": (0, -1), "R": (0, 1)}
MIN_COST = min(TERRAIN.values())   # = 1
MAX_COST = max(TERRAIN.values())   # = 8


class Node:
    __slots__ = ("state", "parent", "action", "g")

    def __init__(self, state, parent=None, action=None, g=0):
        self.state, self.parent, self.action, self.g = state, parent, action, g

    def path(self):
        node, out = self, []
        while node.parent is not None:
            out.append(node.action)
            node = node.parent
        return out[::-1]


class GridProblem:
    """A weighted grid. State is an (row, col) tuple."""

    def __init__(self, grid):
        # grid: list[str], all rows equal length. Contains exactly one S and one G.
        self.grid = grid
        self.rows, self.cols = len(grid), len(grid[0])
        self.initial = self._find("S")
        self.goal = self._find("G")

    def _find(self, ch):
        for r, row in enumerate(self.grid):
            c = row.find(ch)
            if c != -1:
                return (r, c)
        raise ValueError(f"grid has no {ch!r}")

    def _in_bounds(self, r, c):
        return 0 <= r < self.rows and 0 <= c < self.cols

    def cost_of(self, state):
        r, c = state
        return TERRAIN[self.grid[r][c]]

    def actions(self, state):
        r, c = state
        return tuple(m for m, (dr, dc) in MOVES.items()
                     if self._in_bounds(r + dr, c + dc))

    def result(self, state, action):
        dr, dc = MOVES[action]
        return (state[0] + dr, state[1] + dc)

    def is_goal(self, state):
        return state == self.goal

    def step_cost(self, state, action):
        return self.cost_of(self.result(state, action))


def astar(problem, h):
    """Unchanged from the notebook. Returns (goal_node, expansions)."""
    start = Node(problem.initial)
    frontier = [(h(problem, start.state), 0, start)]   # (f, tiebreak, node)
    best_g = {problem.initial: 0}
    expansions, tiebreak = 0, 0
    while frontier:
        _, _, node = heapq.heappop(frontier)
        if problem.is_goal(node.state):
            return node, expansions
        if node.g > best_g.get(node.state, float("inf")):
            continue                                    # stale entry
        expansions += 1
        for action in problem.actions(node.state):
            s2 = problem.result(node.state, action)
            g2 = node.g + problem.step_cost(node.state, action)
            if g2 < best_g.get(s2, float("inf")):
                best_g[s2] = g2
                tiebreak += 1
                heapq.heappush(frontier,
                               (g2 + h(problem, s2), tiebreak,
                                Node(s2, node, action, g2)))
    return None, expansions


# ---- instance loading -------------------------------------------------------

def load_instances(path=None):
    """Load the provided instance bank as {size: [grid, ...]} where each grid is
    a list[str]. See instances.json (generated with a fixed seed)."""
    path = Path(path or Path(__file__).with_name("instances.json"))
    data = json.loads(path.read_text())
    return {int(k): v for k, v in data["instances"].items()}


def render(grid):
    return "\n".join(" ".join(row) for row in grid)
