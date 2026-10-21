"""Duel 1 / Part 2 — the 8-puzzle domain.

Only what is specific to the 8-puzzle lives here: the prompts, the output
parser, the A* tool, and how an answer is validated. The duel itself is in
``duel_core.py``; ``duel.py`` runs this domain and ``duel_grid.py`` through it.

Bank: ``instances_puzzle.json`` (seed 20260807), optimal depths 4 / 8 / 12 /
16, ten each. An answer is ``{"moves": [...], "cost": n}`` where the moves are
moves of the BLANK (U/D/L/R); the tool call is
``{"tool": "astar", "state": [9 numbers]}``.

Two prompt versions exist; ``duel.py`` runs both (v1 replays from the cache)
and writes them to the same files in results/duel/puzzle/, told apart by the
``prompt`` column:

    v2  (main) the format example is a placeholder, ["<move>", ...].
    v1  our first run. Its format example was ["U", "L", ...], and the model
        copied it: 37/40 tool-arm answers began with "U", "L" whatever A*
        returned. Kept as evidence (REPORT §5).

The prompt texts below are frozen: they are part of the cache key of every
transcript in ``.llm_cache/``.
"""

from __future__ import annotations

import json
from pathlib import Path

from duel_core import json_objects
from engine import search as _search
from search import EightPuzzle, load_instances
from starter import h_manhattan
from validator import PUZZLE_GOAL, puzzle_optimal_cost, validate_puzzle

RULES = """You are solving an 8-puzzle.

The board is 3x3 with tiles 1-8 and one blank, shown as _ . Rows are numbered 0-2 from the top, columns 0-2 from the left.
A move slides the BLANK one square: U (up), D (down), L (left) or R (right). The tile in that square moves into the blank's old place.
The blank cannot leave the board. Every move costs 1, so the cost of a solution is its number of moves.

Current board:
{board}

Goal board:
{goal}

As lists (row by row, 0 = blank): current = {state}, goal = {goal_list}.
"""

LLM_TASK = """Find the SHORTEST sequence of moves that turns the current board into the goal board.

Reply with ONLY a JSON object, no explanation, in exactly this format:
{"moves": ["U", "L", ...], "cost": <number of moves>}"""

TOOL_TASK = """Find the SHORTEST sequence of moves that turns the current board into the goal board.

You have a tool that runs an optimal A* search for this puzzle:
  astar(state) -> the shortest move sequence from state to the goal and its cost.
To call it, reply with ONLY this JSON object and nothing else:
{"tool": "astar", "state": [9 numbers, row by row, 0 = blank]}
You will then receive the tool result. After that, reply with ONLY your final answer as a JSON object:
{"moves": ["U", "L", ...], "cost": <number of moves>}"""

TOOL_FOLLOWUP = """

YOUR REPLY:
{reply}

TOOL RESULT:
{result}

Now reply with ONLY your final answer as a JSON object:
{{"moves": ["U", "L", ...], "cost": <number of moves>}}"""

# The format example inside the three templates above, per prompt version.
FORMAT_EXAMPLE = {"v1": '["U", "L", ...]', "v2": '["<move>", "<move>", ...]'}
PROMPT_NOTES = {
    "v2": " — main run (format example is a placeholder)",
    "v1": " — archived first run (format example copied by the model; REPORT §5)",
}


def render(state) -> str:
    return "\n".join("  " + " ".join("_" if v == 0 else str(v)
                                     for v in state[r:r + 3])
                     for r in range(0, 9, 3))


def base_prompt(state) -> str:
    return RULES.format(board=render(state), goal=render(PUZZLE_GOAL),
                        state=list(state), goal_list=list(PUZZLE_GOAL))


def parse_answer(text: str):
    """(moves, reported_cost) from the LAST JSON object with a "moves" key."""
    for obj in reversed(json_objects(text)):
        if "moves" in obj:
            m = obj["moves"]
            return (m if isinstance(m, (list, str)) else None), obj.get("cost")
    return None, None


def parse_tool_call(text: str):
    for obj in json_objects(text):
        if obj.get("tool") == "astar" or ("state" in obj and "moves" not in obj):
            return obj
    return None


def _solvable(state) -> bool:
    tiles = [v for v in state if v != 0]
    inv = sum(1 for i in range(8) for j in range(i + 1, 8) if tiles[i] > tiles[j])
    return inv % 2 == 0


def node_moves(node) -> list[str]:
    states = []
    while node is not None:
        states.append(node.state)
        node = node.parent
    states.reverse()
    step = {-3: "U", 3: "D", -1: "L", 1: "R"}
    return [step[b.index(0) - a.index(0)] for a, b in zip(states, states[1:])]


def run_astar_tool(call: dict) -> tuple[dict, int]:
    """OUR A*, from whatever state the model passes. Returns (result, expansions)."""
    raw = call.get("state")
    if isinstance(raw, list) and raw and all(isinstance(r, list) for r in raw):
        raw = [v for row in raw for v in row]          # accept a 3x3 nesting
    try:
        state = tuple(int(v) for v in raw)
    except (TypeError, ValueError):
        return {"error": "state must be a list of 9 numbers, 0 = blank"}, 0
    if sorted(state) != list(range(9)):
        return {"error": f"{list(state)} is not a permutation of 0-8"}, 0
    if not _solvable(state):
        return {"error": f"{list(state)} cannot reach the goal (odd parity)"}, 0
    res = _search(EightPuzzle(state), "astar", h=h_manhattan)
    return {"moves": node_moves(res.node), "cost": res.cost}, res.expansions


class PuzzleDomain:
    """Mirrors ``duel_grid.GridDomain``; ``prompt`` picks v2 (default) or v1."""

    folder = "puzzle"
    sizes = [4, 8, 12, 16]
    answer_key = "moves"
    repro_tool_size = 8

    def __init__(self, prompt: str = "v2"):
        if prompt not in FORMAT_EXAMPLE:
            raise ValueError(prompt)
        self.prompt = prompt
        self.name = f"puzzle {prompt}"
        self.prompt_note = PROMPT_NOTES[prompt]

    def _fmt(self, text: str) -> str:
        return text.replace(FORMAT_EXAMPLE["v1"], FORMAT_EXAMPLE[self.prompt])

    def size_label(self, size) -> str:
        return f"depth {size}"

    def instances(self):
        states = load_instances(Path(__file__).with_name("instances_puzzle.json"))
        for depth in self.sizes:
            for idx, state in enumerate(states[depth]):
                opt = puzzle_optimal_cost(state)
                assert opt == depth, (depth, idx, opt)    # bank depths are BFS-verified
                yield depth, idx, state, opt

    def llm_prompt(self, state) -> str:
        return base_prompt(state) + "\n" + self._fmt(LLM_TASK)

    def tool_prompt(self, state) -> str:
        return base_prompt(state) + "\n" + self._fmt(TOOL_TASK)

    def followup(self, reply: str, result: dict) -> str:
        return self._fmt(TOOL_FOLLOWUP.format(reply=reply, result=json.dumps(result)))

    parse_answer = staticmethod(parse_answer)
    parse_tool_call = staticmethod(parse_tool_call)
    validate = staticmethod(validate_puzzle)

    def run_tool(self, state, call):
        return run_astar_tool(call)

    def solve_classical(self, state):
        res = _search(EightPuzzle(state), "astar", h=h_manhattan)
        return node_moves(res.node), res.cost, res.expansions

    def show(self, state) -> str:
        return render(state)
