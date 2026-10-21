"""Week 4 Task 2 helpers — the LLM-vs-A* duel on the same instance bank.

You do not need to modify anything below. Fill in ``call_llm`` in your own
script (or use ``aicourse.llm.LLM`` directly) and pass its outputs to
``score_llm_reply`` on each instance. The categories match the lesson plan
exactly:

    illegal        — path is not contiguous or goes out of bounds
    suboptimal     — legal path but total cost > A*'s optimum
    wrong_cost     — legal & optimal path but the reported cost is wrong
    correct        — legal, optimal, and correctly self-reported

The third category is the interesting one — models frequently produce a
correct path with an incorrect self-reported cost. **Never trust the model's
self-reported cost; always recompute with the checker.**
"""
from dataclasses import dataclass
from typing import Optional

from gridworld import GridProblem, MOVES, TERRAIN, astar, load_instances, render


def prompt_for(grid) -> str:
    """The exact prompt from the lesson plan."""
    return (
        "Find the minimum-cost path from S to G.\n"
        "Terrain costs: '.' = 1, ',' = 3, '~' = 8.\n"
        "Move up/down/left/right only.\n"
        "Grid:\n" + render(grid) + "\n\n"
        "Reply with the path as a sequence of moves (U/D/L/R) and its total cost.\n"
        "Format your final answer as two lines:\n"
        "PATH: <letters, no separators>\n"
        "COST: <integer>\n"
    )


@dataclass
class Scored:
    category: str          # 'illegal' | 'suboptimal' | 'wrong_cost' | 'correct'
    llm_path: Optional[str]
    llm_reported_cost: Optional[int]
    checker_cost: Optional[int]
    optimal_cost: int


def _walk(grid, path: str):
    """Return (end_state, total_cost) or (None, None) if illegal."""
    prob = GridProblem(grid)
    state = prob.initial
    total = 0
    for ch in path:
        if ch not in MOVES:
            return None, None
        dr, dc = MOVES[ch]
        r, c = state[0] + dr, state[1] + dc
        if not (0 <= r < prob.rows and 0 <= c < prob.cols):
            return None, None
        state = (r, c)
        total += TERRAIN[prob.grid[r][c]]
    return state, total


def score_llm_reply(grid, llm_path: str, llm_reported_cost: int) -> Scored:
    prob = GridProblem(grid)
    node, _ = astar(prob, lambda p, st: 0)         # ground-truth optimum
    optimal = node.g
    end, checker_cost = _walk(grid, (llm_path or "").strip().upper())
    if end is None or end != prob.goal:
        return Scored("illegal", llm_path, llm_reported_cost, checker_cost, optimal)
    if checker_cost > optimal:
        return Scored("suboptimal", llm_path, llm_reported_cost, checker_cost, optimal)
    if llm_reported_cost != checker_cost:
        return Scored("wrong_cost", llm_path, llm_reported_cost, checker_cost, optimal)
    return Scored("correct", llm_path, llm_reported_cost, checker_cost, optimal)


def parse_reply(text: str):
    """Extract PATH: and COST: lines. Returns (path, cost) or (None, None)."""
    path, cost = None, None
    for line in text.splitlines():
        line = line.strip()
        if line.upper().startswith("PATH:"):
            path = line.split(":", 1)[1].strip().upper().replace(" ", "")
        elif line.upper().startswith("COST:"):
            try:
                cost = int(line.split(":", 1)[1].strip())
            except ValueError:
                cost = None
    return path, cost


if __name__ == "__main__":
    # Demo: score a hand-crafted (wrong) reply to show the pipeline works.
    grid = load_instances()[5][0]
    print("Sample 5x5 grid:")
    print(render(grid))
    print("\nGround-truth optimum via A*:",
          astar(GridProblem(grid), lambda p, st: 0)[0].g)
    # Deliberately illegal reply
    scored = score_llm_reply(grid, "RRRRRR", 6)
    print("Scored illegal reply:", scored)
