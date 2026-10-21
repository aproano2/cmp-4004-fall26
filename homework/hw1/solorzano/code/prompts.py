"""Prompts para el LLM solo y para el LLM con herramienta.
Los dos reciben el mismo enunciado y el mismo formato de respuesta; el brazo con herramienta agrega la descripción de A*
"""
import json

GOAL_TEXT = "1 2 3\n4 5 6\n7 8 _"


def board_text(state):
    return "\n".join(" ".join("_" if v == 0 else str(v) for v in state[i:i + 3]) for i in (0, 3, 6))


def grid_text(rows):
    return "\n".join(" ".join(row) for row in rows)  


def problem_8puzzle(inst):
    return (
        "Solve this 8-puzzle. The board is 3x3; `_` is the blank.\n\n"
        f"Start:\n{board_text(inst['start'])}\n\n"
        f"Goal:\n{GOAL_TEXT}\n\n"
        "A move slides the blank Up (U), Down (D), Left (L) or Right (R), swapping it with the "
        "neighbouring tile. Every move costs 1. Find a SHORTEST sequence of moves that turns Start into Goal.\n\n"
        "You may reason first. Then end your reply with ONE line of JSON, exactly in this form:\n"
        '{"path": "UDLR...", "cost": <number of moves>}'
    )


def problem_grid(inst):
    rows = inst["rows"]
    n = len(rows)
    return (
        f"Weighted grid pathfinding on a {n}x{n} grid. Coordinates are (row, col), 0-indexed; "
        "row 0 is the top row and col 0 is the left column.\n\n"
        "Terrain: `.` road costs 1, `,` grass costs 3, `~` water costs 8, `S` = start, `G` = goal (costs 1). "
        "You pay a cell's cost every time you ENTER it; the start cell is not paid.\n"
        "Moves: up, down, left, right only (no diagonals). Every cell is walkable.\n\n"
        f"Grid:\n{grid_text(rows)}\n\n"
        "Find a path from S to G with MINIMUM total cost (the sum of the costs of every cell you enter).\n\n"
        "You may reason first. Then end your reply with ONE line of JSON, exactly in this form, listing "
        "every cell from S to G inclusive:\n"
        '{"path": [[r, c], [r, c], ...], "cost": <total cost>}'
    )


def problem_text(inst):
    return problem_8puzzle(inst) if inst["domain"] == "8puzzle" else problem_grid(inst)

#Tool arm, protocol "text" (v1, first run). Kept UNCHANGED so the v1 transcripts in .llm_cache/ stay reproducible. Known flaws found after running it (see report):
# * the 8-puzzle example board [2,8,3,1,6,4,7,0,5] is NOT solvable with our goal;
# * the tool is only described in prose, and the user message ends by asking for the
#answer JSON, so a 3B model just answers directly (it called the tool 1/80 times).

TOOL_INSTRUCTIONS = """You have access to one tool: `astar`, an exact A* search implementation.
To call it, reply with ONLY a JSON object (no other text), like this:
- 8-puzzle: {"tool": "astar", "args": {"start": [2,8,3,1,6,4,7,0,5]}} (`start` = the 9 tiles row by row, 0 = blank; the goal is always [1,2,3,4,5,6,7,8,0])
- grid:     {"tool": "astar", "args": {"grid": ["S.,~...", "..."]}} (`grid` = the rows exactly as in the problem, each row as one string WITHOUT spaces)
The tool replies with {"path": ..., "cost": ...} or {"error": ...}. After the tool result arrives, give
your final answer in the required JSON format. You may also answer directly without calling the tool."""

#Tool arm, protocol "native" (v2, default): Ollama's tool-calling API, which uses the function-calling format qwen2.5 was trained on. No example boards in the prompt

NATIVE_SYSTEM = ("You can call the `astar` tool, an exact A* search implementation, to solve the problem. "
                 "Pass the problem exactly as it is given. When you receive the tool result, reply with the "
                 "final answer in the JSON format requested by the user.")

NATIVE_TOOLS = {
    "8puzzle": [{"type": "function", "function": {
        "name": "astar",
        "description": "Exact A* search for the 8-puzzle with goal 1 2 3 / 4 5 6 / 7 8 _. "
                       "Returns {\"path\": moves of the blank as a U/D/L/R string, \"cost\": number of moves}.",
        "parameters": {"type": "object", "required": ["start"], "properties": {
            "start": {"type": "array", "items": {"type": "integer"},
                      "description": "The 9 tiles of the start board row by row, using 0 for the blank `_`."}}}}}],
    "grid": [{"type": "function", "function": {
        "name": "astar",
        "description": "Exact A* search for minimum-cost weighted grid pathfinding (. = 1, , = 3, ~ = 8, S start, "
                       "G goal). Returns {\"path\": list of [row, col] cells from S to G, \"cost\": total cost}.",
        "parameters": {"type": "object", "required": ["grid"], "properties": {
            "grid": {"type": "array", "items": {"type": "string"},
                     "description": "The rows of the grid from top to bottom, one string per row."}}}}}],
}

def native_tool_messages(inst):
    return [{"role": "system", "content": NATIVE_SYSTEM},
            {"role": "user", "content": problem_text(inst)}]

def native_tool_result_messages(content, call, result):
    """Assistant turn that made the call + the tool's reply, in Ollama's chat format."""
    return [{"role": "assistant", "content": content or "",
             "tool_calls": [{"function": {"name": call["name"], "arguments": call["arguments"]}}]},
            {"role": "tool", "tool_name": "astar", "content": json.dumps(result)}]

def llm_messages(inst):
    return [{"role": "user", "content": problem_text(inst)}]

def tool_messages(inst):
    return [{"role": "system", "content": TOOL_INSTRUCTIONS},
            {"role": "user", "content": problem_text(inst)}]

def tool_result_message(result):
    return {"role": "user",
            "content": "Tool result: " + json.dumps(result) +
                       "\nNow give your final answer as the required JSON line."}