"""Duel 1 / Part 2 — the weighted-grid domain.

Only what is specific to grids lives here: the prompts, the output parser, the
A* tool, and how an answer is validated. The duel itself (LLM calls, the tool
loop, aggregation, output files) is in ``duel_core.py``; ``duel.py`` runs this
domain and ``duel_puzzle.py`` through it.

Bank: ``instances.json`` (seed 20260807), 5x5 / 8x8 / 12x12 / 16x16, ten each.
An answer is ``{"path": [[row, col], ...], "cost": n}``; the tool call is
``{"tool": "astar", "start": [r, c], "goal": [r, c]}``.

The prompt texts below are frozen: they are part of the cache key of every
transcript in ``.llm_cache/``, so changing a character would orphan them.
"""

from __future__ import annotations

import json
from pathlib import Path

from duel_core import json_objects
from engine import search as _search
from gridworld import GridProblem, load_instances
from starter import h_manhattan
from validator import find, optimal_cost, validate

RULES = """You are solving a shortest-path problem on a weighted grid.

The grid is {n}x{n}. Rows are numbered from 0 (top) to {last} (bottom), columns from 0 (left) to {last} (right).
Each cell has a terrain type, and you pay the cost of a cell when you ENTER it:
  '.' road  = 1
  ',' grass = 3
  '~' water = 8
  'S' start, 'G' goal = 1
You move one cell per step: up, down, left or right (no diagonal moves), and you must stay inside the grid.
The cost of a path is the sum of the costs of every cell you enter after S (S itself is not charged).

{board}

S is at [{sr}, {sc}]. G is at [{gr}, {gc}].
"""

LLM_TASK = """Find the path from S to G with the LOWEST total cost.

Reply with ONLY a JSON object, no explanation, in exactly this format:
{"path": [[row, col], [row, col], ...], "cost": <total cost>}
The path must list every cell from S to G, both included."""

TOOL_TASK = """Find the path from S to G with the LOWEST total cost.

You have a tool that runs an optimal A* search on THIS grid:
  astar(start, goal) -> the lowest-cost path from start to goal and its cost.
To call it, reply with ONLY this JSON object and nothing else:
{"tool": "astar", "start": [row, col], "goal": [row, col]}
You will then receive the tool result. After that, reply with ONLY your final answer as a JSON object:
{"path": [[row, col], [row, col], ...], "cost": <total cost>}
The path must list every cell from S to G, both included."""

TOOL_FOLLOWUP = """

YOUR REPLY:
{reply}

TOOL RESULT:
{result}

Now reply with ONLY your final answer as a JSON object:
{{"path": [[row, col], [row, col], ...], "cost": <total cost>}}"""


def render(grid) -> str:
    n = len(grid[0])
    head = "     " + "".join(f"{c:>3}" for c in range(n))
    lines = [head] + [f"{r:>3}  " + "".join(f"{ch:>3}" for ch in row)
                      for r, row in enumerate(grid)]
    return "\n".join(lines)


def base_prompt(grid) -> str:
    (sr, sc), (gr, gc) = find(grid, "S"), find(grid, "G")
    n = len(grid)
    return RULES.format(n=n, last=n - 1, board=render(grid),
                        sr=sr, sc=sc, gr=gr, gc=gc)


def llm_prompt(grid) -> str:
    return base_prompt(grid) + "\n" + LLM_TASK


def tool_prompt(grid) -> str:
    return base_prompt(grid) + "\n" + TOOL_TASK


def parse_answer(text: str):
    """(path, reported_cost) from the LAST JSON object with a "path" key, or
    (None, None) if there is none — that is the ``malformed`` category."""
    for obj in reversed(json_objects(text)):
        if "path" in obj:
            path = obj["path"]
            return (path if isinstance(path, list) else None), obj.get("cost")
    return None, None


def parse_tool_call(text: str):
    for obj in json_objects(text):
        if obj.get("tool") == "astar" or ("start" in obj and "goal" in obj
                                          and "path" not in obj):
            return obj
    return None


def node_cells(node) -> list[tuple[int, int]]:
    out = []
    while node is not None:
        out.append(node.state)
        node = node.parent
    return out[::-1]


def run_astar_tool(grid, call: dict) -> tuple[dict, int]:
    """OUR A*, from wherever the model says. Returns (result, expansions)."""
    try:
        start = (int(call["start"][0]), int(call["start"][1]))
        goal = (int(call["goal"][0]), int(call["goal"][1]))
    except (KeyError, TypeError, ValueError, IndexError):
        return {"error": "arguments must be start=[row, col] and goal=[row, col]"}, 0
    n_r, n_c = len(grid), len(grid[0])
    for name, (r, c) in (("start", start), ("goal", goal)):
        if not (0 <= r < n_r and 0 <= c < n_c):
            return {"error": f"{name} {[r, c]} is outside the grid"}, 0
    p = GridProblem(grid)
    p.initial, p.goal = start, goal          # the model chooses the endpoints
    res = _search(p, "astar", h=h_manhattan)
    if not res.solved:
        return {"error": "no path"}, res.expansions
    return {"path": [list(s) for s in node_cells(res.node)], "cost": res.cost}, res.expansions


class GridDomain:
    """The interface ``duel_core`` drives; ``duel_puzzle.PuzzleDomain`` mirrors it."""

    name = folder = "grid"
    prompt, prompt_note = None, ""          # one prompt version only
    sizes = [5, 8, 12, 16]
    answer_key = "path"
    repro_tool_size = 8

    def size_label(self, size) -> str:
        return f"{size}x{size}"

    def instances(self):
        grids = load_instances(Path(__file__).with_name("instances.json"))
        for size in self.sizes:
            for idx, grid in enumerate(grids[size]):
                yield size, idx, grid, optimal_cost(grid)

    llm_prompt = staticmethod(llm_prompt)
    tool_prompt = staticmethod(tool_prompt)
    parse_answer = staticmethod(parse_answer)
    parse_tool_call = staticmethod(parse_tool_call)
    run_tool = staticmethod(run_astar_tool)
    validate = staticmethod(validate)

    def followup(self, reply: str, result: dict) -> str:
        return TOOL_FOLLOWUP.format(reply=reply, result=json.dumps(result))

    def solve_classical(self, grid):
        res = _search(GridProblem(grid), "astar", h=h_manhattan)
        return [list(c) for c in node_cells(res.node)], res.cost, res.expansions

    def show(self, grid) -> str:
        return "\n".join(grid)
