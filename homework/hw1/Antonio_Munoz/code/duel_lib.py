"""duel_lib.py -- prompt, reply parser and OUR OWN validator for the LLM duel (grids).

The validator never asks the model anything. It walks the proposed path itself:
  1. legal?   valid letters, in bounds, no walls, starts at S and ends at G
  2. cost     recomputed by summing the terrain cost of every cell ENTERED
  3. optimal? compared with the optimum from our A* (engine.py)
Categories: correct | illegal | suboptimal | wrong_cost | malformed
"""
import re

import engine
import gridworld as GW
import heuristics_grid as HG

COST = {".": 1, ",": 3, "~": 8, "G": 1, "S": 1}     # our own copy (cost paid on ENTERING)
MOVES = {"U": (-1, 0), "D": (1, 0), "L": (0, -1), "R": (0, 1)}


def prompt_for(grid, variant="direct"):
    """variant 'direct' (main arm): answer only, no explanation.
    variant 'free': the model may reason before answering (course-style prompt)."""
    head = (
        "Find the minimum-cost path from S to G.\n"
        "Terrain costs: '.' = 1, ',' = 3, '~' = 8.\n"
        "Move up/down/left/right only (U = up, toward the first row; D = down; "
        "L = left; R = right).\n"
        "The cost of a path is the sum of the terrain cost of every cell you enter "
        "(S itself is not counted; G costs 1).\n"
        "Grid:\n" + "\n".join(" ".join(row) for row in grid) + "\n\n"
    )
    if variant == "direct":
        tail = ("Do not explain and do not show your reasoning. Reply with exactly "
                "two lines and nothing else:\n"
                "PATH: <letters U/D/L/R, no separators>\n"
                "COST: <integer>\n")
    else:
        tail = ("Reply with the path as a sequence of moves (U/D/L/R) and its total "
                "cost.\nFormat your final answer as two lines:\n"
                "PATH: <letters, no separators>\n"
                "COST: <integer>\n")
    return head + tail


def parse_reply(text):
    """Return (path, cost). path is None if no 'PATH:' is found. The LAST occurrence
    wins (the model may think out loud before the final answer)."""
    paths = re.findall(r"PATH[\s*`_]*:[\s*`_]*([^\n]*)", text, flags=re.I)
    costs = re.findall(r"COST[\s*`_]*:[\s*`_]*(-?\d+)", text, flags=re.I)
    path = re.sub(r"[\s,`*\-]", "", paths[-1]).upper() if paths else None
    cost = int(costs[-1]) if costs else None
    return path, cost


def _find(grid, ch):
    for r, row in enumerate(grid):
        if ch in row:
            return (r, row.index(ch))
    raise ValueError(f"no {ch} in grid")


def walk(grid, path):
    """Walk `path` from S. Returns (ok, reason, cost). reason is None when legal."""
    rows, cols = len(grid), len(grid[0])
    r, c = _find(grid, "S")
    goal = _find(grid, "G")
    if not path:
        return False, "empty_path", None
    total = 0
    for ch in path:
        if ch not in MOVES:
            return False, "invalid_char", None
        dr, dc = MOVES[ch]
        r, c = r + dr, c + dc
        if not (0 <= r < rows and 0 <= c < cols):
            return False, "out_of_bounds", None
        cell = grid[r][c]
        if cell == "#":
            return False, "wall", None
        total += COST[cell]
    if (r, c) != goal:
        return False, "not_at_goal", None
    return True, None, total


def optimal_cost(grid):
    """Optimum from our A* (admissible heuristic -> optimal, see analysis 1)."""
    res = engine.run(GW.GridProblem(grid), "astar", HG.h_manhattan_scaled, timeout=60)
    assert res["status"] == "ok"
    return res["cost"]


def validate(grid, reply_text, optimal=None):
    """Classify one reply. Returns a dict (one CSV row's worth of fields)."""
    path, reported = parse_reply(reply_text)
    out = {"path": path, "reported_cost": reported, "category": None, "reason": None,
           "true_cost": None, "optimal_cost": None, "cost_reported_ok": None}
    if path is None:
        out.update(category="malformed", reason="no_PATH_found")
        return out
    ok, reason, true_cost = walk(grid, path)
    if not ok:
        out.update(category="illegal", reason=reason)
        return out
    opt = optimal if optimal is not None else optimal_cost(grid)
    assert true_cost >= opt, "legal path cheaper than the optimum: validator or A* bug"
    out.update(true_cost=true_cost, optimal_cost=opt,
               cost_reported_ok=(reported == true_cost))
    if true_cost > opt:
        out["category"] = "suboptimal"
    elif reported != true_cost:
        out["category"] = "wrong_cost"
    else:
        out["category"] = "correct"
    return out
