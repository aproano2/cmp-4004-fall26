"""Part 2 (the duel) -- shared pieces: instances, prompts, parser, VALIDATOR.

The validator is plain code. The model is never asked whether its own answer is
correct. It checks, in this order:
    1. parseable?   2. every move legal (in bounds / blank can move)?
    3. does the path end at the goal?   4. recomputed cost vs. reported cost
    5. recomputed cost vs. optimal cost from YOUR A*.
"""
import json
import re
from pathlib import Path

from search import astar
from eight_puzzle import EightPuzzle, GOAL_STATE
from gridworld import GridProblem, render, TERRAIN
from heuristics import h_manhattan

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RESULTS_DIR = ROOT / "results"
FIG_DIR = ROOT / "fig"
CACHE_DIR = ROOT / ".llm_cache"
GRID_FILE = HERE / "data" / "instances.json"
PUZZLE_FILE = HERE / "data" / "puzzle_instances.json"

# Bump this string whenever you change ANY prompt text. It is part of the
# cache key, so old transcripts are never silently reused.
PROMPT_VERSION = "v2"

PUZZLE_MOVES = ("UP", "DOWN", "LEFT", "RIGHT")
GRID_MOVES = ("U", "D", "L", "R")
SHORT = {"UP": "U", "DOWN": "D", "LEFT": "L", "RIGHT": "R"}
LONG = {v: k for k, v in SHORT.items()}


# --------------------------------------------------------------------------
# Instances
# --------------------------------------------------------------------------

def load_instances(domain, per_level=10):
    """Return a list of dicts: {domain, level, idx, data}.

    domain 'puzzle': data = tuple of 9 ints.   domain 'grid': data = list[str].
    """
    out = []
    if domain == "puzzle":
        d = json.loads(PUZZLE_FILE.read_text())
        for lvl in d["depths"]:
            for i, s in enumerate(d["instances"][str(lvl)][:per_level]):
                out.append(dict(domain="puzzle", level=lvl, idx=i, data=tuple(s)))
    elif domain == "grid":
        d = json.loads(GRID_FILE.read_text())
        for lvl in d["sizes"]:
            for i, g in enumerate(d["instances"][str(lvl)][:per_level]):
                out.append(dict(domain="grid", level=lvl, idx=i, data=list(g)))
    else:
        raise ValueError(domain)
    return out


def make_problem(inst):
    return EightPuzzle(inst["data"]) if inst["domain"] == "puzzle" else GridProblem(inst["data"])


def _grid_h(problem):
    gr, gc = problem.goal
    return lambda s: abs(s[0] - gr) + abs(s[1] - gc)


def reference_solution(inst):
    """Optimal (cost, moves) from YOUR A*. This is the ground truth."""
    p = make_problem(inst)
    h = h_manhattan if inst["domain"] == "puzzle" else _grid_h(p)
    node, exp, _ = astar(p, h)
    return node.g, node.path()


# --------------------------------------------------------------------------
# Prompts  (ONE fixed prompt per domain: do not tune per instance)
# --------------------------------------------------------------------------

SYSTEM = "You are an expert at search and planning problems. Be precise."

_FORMAT_TAIL = (
    "You may reason step by step first. Then END your reply with exactly one "
    "JSON object on its own line and nothing after it, in this format:\n"
)


def puzzle_prompt(state):
    b = lambda s: "\n".join(" ".join(map(str, s[i:i + 3])) for i in (0, 3, 6))
    return (
        "Solve this 8-puzzle with the FEWEST possible moves.\n\n"
        f"Current board (0 is the blank):\n{b(state)}\n\n"
        f"Goal board:\n{b(GOAL_STATE)}\n\n"
        "A move slides the blank into an adjacent cell (it swaps places with the "
        "tile there). Moves are named by the direction the BLANK moves: "
        "UP, DOWN, LEFT, RIGHT. The blank cannot leave the 3x3 board. "
        "Every move costs 1, so the total cost equals the number of moves.\n\n"
        + _FORMAT_TAIL
        + '{"moves": ["UP", "LEFT", ...], "cost": <total cost as an integer>}'
    )


def grid_prompt(grid):
    p = GridProblem(grid)
    return (
        "Find a MINIMUM-COST path on this weighted grid from S to G.\n\n"
        f"Grid (row 0 is the top, column 0 is the left):\n{render(grid)}\n\n"
        f"S is at (row, col) = {p.initial}. G is at (row, col) = {p.goal}.\n"
        "Terrain cost is charged when you ENTER a cell: '.' = 1, ',' = 3, "
        "'~' = 8, 'G' = 1. The starting cell costs nothing. "
        "There are no walls, but you cannot leave the grid.\n"
        "Moves: U = row-1, D = row+1, L = col-1, R = col+1. "
        "The path cost is the sum of the costs of all cells you enter.\n\n"
        + _FORMAT_TAIL
        + '{"moves": ["R", "D", ...], "cost": <total cost as an integer>}'
    )


def build_prompt(inst):
    return puzzle_prompt(inst["data"]) if inst["domain"] == "puzzle" else grid_prompt(inst["data"])


TOOL_SYSTEM = (
    "You are an expert search assistant using a tool.\n\n"
    "You have ONE tool: astar_solve.\n"
    "IMPORTANT: You MUST call the tool before giving your final answer.\n"
    "Do NOT solve the puzzle yourself.\n"
    "Do NOT output a solution before the tool is called.\n\n"
    "Your first response MUST be ONLY one JSON object, with no explanation:\n"
    '{"tool":"astar_solve","arguments":{"state":[9 integers, row-major, 0 = blank]}}\n'
    "For a grid, use:\n"
    '{"tool":"astar_solve","arguments":{"grid":["row0","row1",...]}}\n'
    "\n"
    "After receiving the tool result, give your final answer using the exact "
    "JSON format requested by the task."
)


# --------------------------------------------------------------------------
# Parsing
# --------------------------------------------------------------------------

def _json_objects(text):
    """Yield every balanced {...} substring of text that json-parses to a dict."""
    depth, start = 0, None
    for i, ch in enumerate(text):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}" and depth:
            depth -= 1
            if depth == 0:
                try:
                    obj = json.loads(text[start:i + 1])
                    if isinstance(obj, dict):
                        yield obj
                except Exception:
                    pass


def parse_answer(text):
    """Last JSON object with a 'moves' key -> (moves_tokens, cost) or None."""
    found = [o for o in _json_objects(text or "") if "moves" in o]
    if not found:
        return None
    o = found[-1]
    m = o["moves"]
    if isinstance(m, str):
        m = re.findall(r"UP|DOWN|LEFT|RIGHT|U|D|L|R", m.upper())
    elif isinstance(m, list):
        m = [str(x).strip().upper() for x in m]
    else:
        return None
    cost = o.get("cost")
    try:
        cost = int(cost) if cost is not None and not isinstance(cost, bool) else None
    except (TypeError, ValueError):
        cost = None
    return m, cost


def parse_tool_call(text):
    for o in _json_objects(text or ""):
        if o.get("tool") and isinstance(o.get("arguments"), dict):
            return o
    return None


def normalize_moves(domain, moves):
    """Map aliases (U<->UP) to the domain's canonical names; unknown -> as-is."""
    out = []
    for m in moves:
        if domain == "puzzle":
            out.append(LONG.get(m, m))
        else:
            out.append(SHORT.get(m, m))
    return out


# --------------------------------------------------------------------------
# VALIDATOR
# --------------------------------------------------------------------------

def validate(inst, text, ref_cost=None):
    """Classify one model answer. Never consults the model.

    category:
        optimal_correct  -> legal, optimal, reported cost right   (a "win")
        illegal          -> unparseable / illegal move / does not end at goal
        suboptimal       -> legal, reaches goal, true cost > optimal
        wrong_cost       -> legal AND optimal, but reported cost != true cost
    """
    if ref_cost is None:
        ref_cost, _ = reference_solution(inst)
    r = dict(parsed=False, legal=False, reason="", reported_cost=None,
             true_cost=None, ref_cost=ref_cost, n_moves=None,
             optimal=False, cost_correct=False, category="illegal",
             answer_key="")

    ans = parse_answer(text)
    if ans is None:
        r["reason"] = "unparseable"
        return r
    moves, reported = ans
    r["parsed"], r["reported_cost"] = True, reported
    moves = normalize_moves(inst["domain"], moves)
    r["n_moves"] = len(moves)
    r["answer_key"] = " ".join(moves) + f" |{reported}"

    p = make_problem(inst)
    state, total = p.initial, 0
    for k, mv in enumerate(moves):
        if mv not in p.actions(state):
            r["reason"] = f"illegal move #{k + 1} ({mv}) from {state}"
            return r
        total += p.step_cost(state, mv)
        state = p.result(state, mv)
    if not p.is_goal(state):
        r["reason"] = f"ends at {state}, not at goal"
        return r

    r["legal"] = True
    r["true_cost"] = total
    r["optimal"] = total == ref_cost
    r["cost_correct"] = reported == total
    if not r["optimal"]:
        r["category"] = "suboptimal"
        r["reason"] = f"cost {total} > optimal {ref_cost}"
    elif not r["cost_correct"]:
        r["category"] = "wrong_cost"
        r["reason"] = f"reported {reported}, real {total}"
    else:
        r["category"] = "optimal_correct"
    return r


# --------------------------------------------------------------------------
# The tool given to the model (your A*)
# --------------------------------------------------------------------------

def _solvable(state):
    inv = sum(1 for i in range(9) for j in range(i + 1, 9)
              if state[i] and state[j] and state[i] > state[j])
    return inv % 2 == 0


def execute_tool(inst, call):
    """Run YOUR A* on the arguments the model sent.

    Returns (result_dict, args_match) where args_match says whether the model
    transcribed the real instance correctly.
    """
    args = call.get("arguments", {})
    try:
        if inst["domain"] == "puzzle":
            st = tuple(int(x) for x in args["state"])
            if sorted(st) != list(range(9)):
                return {"error": "state must be a permutation of 0..8"}, False
            if not _solvable(st):
                return {"error": "state is not solvable"}, st == inst["data"]
            problem, h, match = EightPuzzle(st), h_manhattan, st == inst["data"]
        else:
            grid = [str(r) for r in args["grid"]]
            if (not grid or len(grid) > 30 or len({len(r) for r in grid}) != 1
                    or any(ch not in TERRAIN for r in grid for ch in r)
                    or sum(r.count("S") for r in grid) != 1
                    or sum(r.count("G") for r in grid) != 1):
                return {"error": "invalid grid (need equal-length rows, chars . , ~ S G, one S, one G)"}, False
            problem = GridProblem(grid)
            h, match = _grid_h(problem), grid == inst["data"]
        node, exp, _ = astar(problem, h)
        if node is None:
            return {"error": "no solution"}, match
        return {"moves": node.path(), "cost": node.g, "expansions": exp}, match
    except Exception as e:  # malformed arguments
        return {"error": f"bad arguments: {e}"}, False
