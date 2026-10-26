import json
import random
from collections import deque
from pathlib import Path

from eight_puzzle import EightPuzzle, GOAL_STATE


HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "data"

OUTPUT_FILE = DATA_DIR / "puzzle_instances.json"

DEPTHS = [4, 8, 12, 16]
PER_DEPTH = 10
SEED = 20261005


def generate_states_by_depth(max_depth):
    """
    Run BFS outward from the goal state.

    Because BFS discovers states in increasing distance,
    the depth assigned to each state is its optimal
    distance from the goal.
    """

    problem = EightPuzzle(GOAL_STATE)

    frontier = deque([
        (GOAL_STATE, 0)
    ])

    visited = {GOAL_STATE}

    states_by_depth = {
        depth: []
        for depth in range(max_depth + 1)
    }

    states_by_depth[0].append(GOAL_STATE)

    while frontier:

        state, depth = frontier.popleft()

        if depth == max_depth:
            continue

        for action in problem.actions(state):

            child = problem.result(
                state,
                action
            )

            if child in visited:
                continue

            visited.add(child)

            child_depth = depth + 1

            states_by_depth[
                child_depth
            ].append(child)

            frontier.append(
                (child, child_depth)
            )

    return states_by_depth


def choose_instances(states_by_depth):
    """
    Select exactly PER_DEPTH states from each required
    optimal depth using a fixed random seed.
    """

    rng = random.Random(SEED)

    selected = {}

    for depth in DEPTHS:

        candidates = states_by_depth[depth]

        print(
            f"Depth {depth}: "
            f"{len(candidates)} candidate states"
        )

        if len(candidates) < PER_DEPTH:
            raise ValueError(
                f"Not enough states at depth {depth}"
            )

        chosen = rng.sample(
            candidates,
            PER_DEPTH
        )

        # JSON does not have tuples, so convert them
        # to lists before saving.
        selected[str(depth)] = [
            list(state)
            for state in chosen
        ]

    return selected


def main():

    DATA_DIR.mkdir(exist_ok=True)

    print("Generating 8-puzzle state space...")

    states_by_depth = generate_states_by_depth(
        max(DEPTHS)
    )

    instances = choose_instances(
        states_by_depth
    )

    output = {
        "seed": SEED,
        "depths": DEPTHS,
        "per_depth": PER_DEPTH,
        "goal": list(GOAL_STATE),
        "instances": instances,
    }

    with open(
        OUTPUT_FILE,
        "w"
    ) as f:

        json.dump(
            output,
            f,
            indent=2
        )

    print()
    print(f"Saved: {OUTPUT_FILE}")

    print(
        "Total selected:",
        sum(
            len(states)
            for states in instances.values()
        )
    )


if __name__ == "__main__":
    main()