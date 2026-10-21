"""Instance generator for week-4 studio. Run once at build time; commits
``instances.json`` alongside. Deterministic (SEED=20260807).

Instances are guaranteed *solvable* (a path of finite cost exists) and are
non-trivial (start != goal, not adjacent). We don't guarantee any particular
optimal-cost distribution — the point of the studio is to *measure*.
"""
import json
import random
from pathlib import Path

from gridworld import GridProblem, astar

SEED = 20260807
SIZES = [5, 8, 12, 16]
PER_SIZE = 10
# Terrain distribution: mostly road, some grass, a little water.
WEIGHTS = {".": 0.60, ",": 0.28, "~": 0.12}


def random_grid(n, rng):
    while True:
        cells = [
            [rng.choices(list(WEIGHTS), weights=list(WEIGHTS.values()))[0]
             for _ in range(n)]
            for _ in range(n)
        ]
        # S in top-left region, G in bottom-right region — non-trivial distance.
        sr, sc = rng.randint(0, n // 2 - 1) if n > 2 else 0, rng.randint(0, n // 2 - 1) if n > 2 else 0
        gr, gc = rng.randint(n // 2, n - 1), rng.randint(n // 2, n - 1)
        if (sr, sc) == (gr, gc):
            continue
        cells[sr][sc] = "S"
        cells[gr][gc] = "G"
        grid = ["".join(row) for row in cells]
        # solvability check (all-1 grids are always solvable; keep the check
        # anyway — it's cheap and future-proof if we ever add walls)
        prob = GridProblem(grid)
        node, _ = astar(prob, lambda p, s: 0)
        if node is not None:
            return grid


def main():
    rng = random.Random(SEED)
    out = {"seed": SEED, "sizes": SIZES, "per_size": PER_SIZE, "instances": {}}
    for n in SIZES:
        out["instances"][str(n)] = [random_grid(n, rng) for _ in range(PER_SIZE)]
    dest = Path(__file__).with_name("instances.json")
    dest.write_text(json.dumps(out, indent=2))
    print(f"wrote {dest} — {sum(len(v) for v in out['instances'].values())} grids")


if __name__ == "__main__":
    main()
