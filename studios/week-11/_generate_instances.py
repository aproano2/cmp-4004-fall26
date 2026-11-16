"""Instance recorder for the week-11 swarm studio. Run once at build time; it
commits ``instances.json`` alongside. Deterministic (SEED = 20250806, the same
seed the Session-A notebook uses).

WHY THIS FILE EXISTS (honest note): unlike week 10's TSP, the Session-A notebook
DOES build its TSP instance in code — ``make_tsp(n_cities=25, seed=SEED)`` — so
the instance is already reproducible from the seed and ``swarm.PTS``/``swarm.DIST``
are the verbatim source of truth. This file simply serialises that same instance
(cities + the nearest-neighbour known-good tour) so students can read the numbers
without running numpy, exactly as ``instances.json`` did in weeks 4 and 10.
Rotate SEED in ``swarm.make_tsp`` and re-run to record a different instance.
"""
import json
from pathlib import Path

from swarm import PTS, NC, SEED, tour_length, nearest_neighbour_tour


def main():
    nn_tour = nearest_neighbour_tour(start=0)
    out = {
        "seed": SEED,
        "n_cities": NC,
        "field": 100.0,
        "cities": [[round(float(x), 4), round(float(y), 4)] for x, y in PTS],
        "nearest_neighbour_tour": nn_tour,
        "nearest_neighbour_length": round(tour_length(nn_tour), 4),
    }
    dest = Path(__file__).with_name("instances.json")
    dest.write_text(json.dumps(out, indent=2))
    print(f"wrote {dest} — {NC} cities, "
          f"NN tour length {out['nearest_neighbour_length']}")


if __name__ == "__main__":
    main()
