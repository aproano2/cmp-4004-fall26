import csv
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))

from aicourse.llm import LLM
from domains import Puzzle, Grid, puzzle_heuristic_manhattan, grid_heuristic
from search_algorithms import astar


MODEL_NAME = "qwen2.5:3b"
model = LLM(backend="ollama")

os.makedirs(".llm_cache", exist_ok=True)
os.makedirs("results", exist_ok=True)

OUTPUT_CSV = "results/llm_responses.csv"


def extract_json(text):
    """Extract a JSON object from the model response."""
    text = text.strip()

    # Remove markdown fences if the model uses them.
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to find the outermost JSON object.
    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except json.JSONDecodeError:
            pass

    return None


def puzzle_prompt(instance):
    return f"""
You are solving an 8-puzzle.

The board is represented as a flat list of 9 integers.
0 represents the blank tile.

Start:
{instance["start"]}

Goal:
{instance["goal"]}

A legal move swaps the blank (0) with exactly one horizontally
or vertically adjacent tile.

Find a legal path from Start to Goal.

Return ONLY valid JSON in exactly this format:

{{
  "path": [
    [state1],
    [state2]
  ]
}}

The path MUST include both the start state and the goal state.
Do not include explanations.
"""


def grid_prompt(instance):
    terrain = instance["terrain"]

    return f"""
You are solving a weighted grid pathfinding problem.

Terrain:
{json.dumps(terrain)}

Start:
{instance["start"]}

Goal:
{instance["goal"]}

You may move only UP, DOWN, LEFT, or RIGHT.
Diagonal movement is forbidden.

The cost of a move is the terrain value of the cell ENTERED.
The starting cell has no entry cost.

Find a minimum-cost path from Start to Goal.

Return ONLY valid JSON in exactly this format:

{{
  "path": [
    [row, column],
    [row, column]
  ],
  "reported_cost": NUMBER
}}

The path MUST include both Start and Goal.
Do not include explanations.
"""


def normalize_path(data):
    if not isinstance(data, dict):
        return None

    path = data.get("path")

    if not isinstance(path, list):
        return None

    try:
        return [tuple(x) for x in path]
    except (TypeError, ValueError):
        return None


def validate_puzzle(path, problem, expected_cost):
    if not path:
        return False, False

    if path[0] != problem.start or path[-1] != problem.goal:
        return False, False

    for current, nxt in zip(path, path[1:]):
        legal_neighbors = [state for state, _ in problem.neighbors(current)]
        if nxt not in legal_neighbors:
            return False, False

    actual_cost = len(path) - 1
    optimal = actual_cost == expected_cost

    return True, optimal


def validate_grid(path, problem, expected_cost):
    if not path:
        return False, False, None

    if path[0] != problem.start or path[-1] != problem.goal:
        return False, False, None

    cost = 0

    for current, nxt in zip(path, path[1:]):
        legal = False

        for neighbor, step_cost in problem.neighbors(current):
            if neighbor == nxt:
                legal = True
                cost += step_cost
                break

        if not legal:
            return False, False, None

    return True, cost == expected_cost, cost


def load_completed():
    completed = set()

    if not os.path.exists(OUTPUT_CSV):
        return completed

    with open(OUTPUT_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            completed.add(
                (row["domain"], int(row["level"]), int(row["instance"]))
            )

    return completed


def save_transcript(domain, level, idx, prompt, response):
    filename = f"{domain}_{level}_{idx}.json"
    path = os.path.join(".llm_cache", filename)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "model": MODEL_NAME,
                "domain": domain,
                "level": level,
                "instance": idx,
                "prompt": prompt,
                "response": response,
            },
            f,
            indent=2,
        )


def run():
    completed = load_completed()

    file_exists = os.path.exists(OUTPUT_CSV)

    fields = [
        "domain",
        "level",
        "instance",
        "model",
        "wall_time_s",
        "parsed",
        "legal",
        "optimal",
        "reported_cost",
        "actual_cost",
        "expected_cost",
        "response",
    ]

    with open(
        OUTPUT_CSV,
        "a",
        newline="",
        encoding="utf-8",
    ) as csvfile:

        writer = csv.DictWriter(csvfile, fieldnames=fields)

        if not file_exists:
            writer.writeheader()
            csvfile.flush()

        # ---------- 8 PUZZLE ----------

        for depth in [4, 8, 12, 16]:

            filename = f"results/instances/puzzle_{depth}.json"

            with open(filename, encoding="utf-8") as f:
                instances = json.load(f)

            for idx, instance in enumerate(instances):

                key = ("8puzzle", depth, idx)

                if key in completed:
                    print("SKIP", key)
                    continue

                problem = Puzzle(tuple(instance["start"]), tuple(instance["goal"]))

                reference = astar(
                    problem,
                    puzzle_heuristic_manhattan,
                    timeout=30,
                )

                expected_cost = reference.cost

                prompt = puzzle_prompt(instance)

                print(f"\nRunning 8puzzle depth={depth} instance={idx}")

                t0 = time.perf_counter()

                try:
                    response = model.complete(prompt).text
                except Exception as e:
                    response = f"MODEL_ERROR: {e}"

                elapsed = time.perf_counter() - t0

                save_transcript(
                    "8puzzle",
                    depth,
                    idx,
                    prompt,
                    response,
                )

                data = extract_json(response)
                path = normalize_path(data)

                parsed = data is not None and path is not None

                legal, optimal = validate_puzzle(
                    path,
                    problem,
                    expected_cost,
                )

                actual_cost = len(path) - 1 if legal else ""

                writer.writerow(
                    {
                        "domain": "8puzzle",
                        "level": depth,
                        "instance": idx,
                        "model": MODEL_NAME,
                        "wall_time_s": elapsed,
                        "parsed": parsed,
                        "legal": legal,
                        "optimal": optimal,
                        "reported_cost": "",
                        "actual_cost": actual_cost,
                        "expected_cost": expected_cost,
                        "response": response,
                    }
                )

                csvfile.flush()

                print(
                    f"  parsed={parsed} legal={legal} "
                    f"optimal={optimal} expected={expected_cost}"
                )

        # ---------- GRID ----------

        for size in [5, 8, 12, 16]:

            filename = f"results/instances/grid_{size}.json"

            with open(filename, encoding="utf-8") as f:
                instances = json.load(f)

            for idx, instance in enumerate(instances):

                key = ("grid", size, idx)

                if key in completed:
                    print("SKIP", key)
                    continue

                terrain = tuple(
                    tuple(row) for row in instance["terrain"]
                )

                problem = Grid(
                    terrain,
                    tuple(instance["start"]),
                    tuple(instance["goal"]),
                )

                reference = astar(
                    problem,
                    grid_heuristic,
                    timeout=30,
                )

                expected_cost = reference.cost

                prompt = grid_prompt(instance)

                print(f"\nRunning grid size={size} instance={idx}")

                t0 = time.perf_counter()

                try:
                    response = model.complete(prompt).text
                except Exception as e:
                    response = f"MODEL_ERROR: {e}"

                elapsed = time.perf_counter() - t0

                save_transcript(
                    "grid",
                    size,
                    idx,
                    prompt,
                    response,
                )

                data = extract_json(response)
                path = normalize_path(data)

                parsed = data is not None and path is not None

                legal, optimal, actual_cost = validate_grid(
                    path,
                    problem,
                    expected_cost,
                )

                reported_cost = ""

                if isinstance(data, dict):
                    reported_cost = data.get("reported_cost", "")

                writer.writerow(
                    {
                        "domain": "grid",
                        "level": size,
                        "instance": idx,
                        "model": MODEL_NAME,
                        "wall_time_s": elapsed,
                        "parsed": parsed,
                        "legal": legal,
                        "optimal": optimal,
                        "reported_cost": reported_cost,
                        "actual_cost": actual_cost if actual_cost is not None else "",
                        "expected_cost": expected_cost,
                        "response": response,
                    }
                )

                csvfile.flush()

                print(
                    f"  parsed={parsed} legal={legal} "
                    f"optimal={optimal} actual={actual_cost} "
                    f"expected={expected_cost}"
                )


if __name__ == "__main__":
    run()