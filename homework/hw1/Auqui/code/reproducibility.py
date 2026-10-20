import json
import os
import sys
import time

# Allow imports from code/
sys.path.insert(0, os.path.dirname(__file__))

from aicourse.llm import LLM


MODEL_NAME = "qwen2.5:3b"
INSTANCE_FILE = "results/instances/grid_5.json"
INSTANCE_INDEX = 8
N_CALLS = 5


def build_prompt(instance):
    terrain = instance["terrain"]
    start = instance["start"]
    goal = instance["goal"]

    return f"""Solve the following weighted grid pathfinding problem.

Terrain:
{json.dumps(terrain)}

Start: {json.dumps(start)}
Goal: {json.dumps(goal)}

Rules:
- You may move only up, down, left, or right.
- Every coordinate must remain inside the grid.
- The cost of a move is the terrain value of the cell ENTERED.
- Do not include the cost of the starting cell.
- Find a minimum-cost path from start to goal.
- Return ONLY valid JSON.
- Do not use Markdown or code fences.

Required format:
{{"path":[[row,column],...],"reported_cost":NUMBER}}
"""


def main():
    with open(INSTANCE_FILE, "r", encoding="utf-8") as f:
        instances = json.load(f)

    instance = instances[INSTANCE_INDEX]
    prompt = build_prompt(instance)

    # IMPORTANT: construct the prompt once.
    # The exact same string is sent on all five calls.
    model = LLM(backend="ollama")

    responses = []
    records = []

    print(f"Model: {MODEL_NAME}")
    print(f"Instance: grid 5x5 #{INSTANCE_INDEX}")
    print(f"Calls: {N_CALLS}")
    print("=" * 60)

    for i in range(N_CALLS):
        print(f"\nCall {i + 1}/{N_CALLS}...")

        start_time = time.perf_counter()
        response = model.complete(prompt).text
        elapsed = time.perf_counter() - start_time

        responses.append(response.strip())

        records.append({
            "call": i + 1,
            "wall_time_s": elapsed,
            "response": response
        })

        print(response)
        print(f"Time: {elapsed:.2f} s")

    distinct = len(set(responses))

    output = {
        "model": MODEL_NAME,
        "domain": "grid",
        "level": 5,
        "instance": INSTANCE_INDEX,
        "identical_calls": N_CALLS,
        "distinct_answers": distinct,
        "prompt": prompt,
        "calls": records
    }

    os.makedirs(".llm_cache", exist_ok=True)

    output_file = ".llm_cache/reproducibility_grid5_instance8.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 60)
    print("REPRODUCIBILITY RESULT")
    print("=" * 60)
    print(f"Identical calls: {N_CALLS}")
    print(f"Distinct answers: {distinct}")
    print(f"Saved to: {output_file}")


if __name__ == "__main__":
    main()