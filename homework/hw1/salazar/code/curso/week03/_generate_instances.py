"""Instance generator for the week-3 studio (8-puzzle). Run once at build time;
commits ``instances.json`` alongside. Deterministic (SEED=20260807).

Method is exactly the notebook's appendix: an exhaustive BFS *backwards from the
goal* labels every one of the 181 440 reachable states with its true optimal
depth. We then sample PER_DEPTH instances at each target depth. Because depths are
read off the exhaustive BFS, every instance's optimal solution length is exact --
never trust a hand-labelled puzzle depth, including these.

The four canonical notebook instances (D8, D12, D16 -> their matching buckets)
are pinned as the first entry of their depth so the notebook data appears
verbatim in the bank.
"""
import json
import random
from collections import deque
from pathlib import Path

from search import EightPuzzle, GOAL, D8, D12, D16

SEED = 20260807
DEPTHS = [4, 8, 12, 16]      # plan Session 3B, Task 3
PER_DEPTH = 10
PINNED = {8: D8, 12: D12, 16: D16}   # notebook constants, verbatim


def true_depths():
    """Exhaustive BFS backwards from GOAL. Returns {state: optimal_depth}."""
    dist = {GOAL: 0}
    q = deque([GOAL])
    pz = EightPuzzle(GOAL)
    while q:
        s = q.popleft()
        for a in pz.actions(s):
            t = pz.result(s, a)
            if t not in dist:
                dist[t] = dist[s] + 1
                q.append(t)
    return dist


def main():
    dist = true_depths()
    print(f"reachable states: {len(dist):,}   hardest: {max(dist.values())} moves")

    by_depth = {d: [] for d in DEPTHS}
    for state, d in dist.items():
        if d in by_depth:
            by_depth[d].append(state)

    rng = random.Random(SEED)
    out = {"seed": SEED, "depths": DEPTHS, "per_depth": PER_DEPTH, "instances": {}}
    for d in DEPTHS:
        pool = sorted(by_depth[d])           # deterministic order before shuffle
        rng.shuffle(pool)
        chosen = pool[:PER_DEPTH]
        if d in PINNED and PINNED[d] not in chosen:
            chosen = [PINNED[d]] + chosen[:PER_DEPTH - 1]
        elif d in PINNED:                    # move the pinned one to the front
            chosen.remove(PINNED[d])
            chosen = [PINNED[d]] + chosen
        # sanity: every chosen instance really has this optimal depth
        for st in chosen:
            assert dist[st] == d, (st, dist[st], d)
        out["instances"][str(d)] = [list(st) for st in chosen]

    dest = Path(__file__).with_name("instances.json")
    dest.write_text(json.dumps(out, indent=2))
    n = sum(len(v) for v in out["instances"].values())
    print(f"wrote {dest} -- {n} instances across depths {DEPTHS}")


if __name__ == "__main__":
    main()
