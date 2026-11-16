"""Week 10 studio — REFERENCE SOLUTION (instructor-only).

A filled-in copy of ``starter.py``: identical function names and signatures, so
the *provided* ``test_localsearch.py`` passes when this module is imported in
place of ``starter``. Verify with ``studios/_verify_solutions.py``.

DO NOT ship this to students — excluded via ``studios/.gitignore``. The teaching
walkthrough lives in ``solution.ipynb`` (which imports this file, never re-pastes
it).

  Task 1  ``order_crossover`` / ``swap_mutation`` — the two TSP genetic operators.
          OX exists because plain one-point crossover splices two permutations
          into repeated/missing cities (an invalid tour); the segment-copy +
          ordered-fill is what guarantees every child is a valid permutation.
  Task 2  ``run_study`` — the 18-config x 5-seed hyperparameter study at a FIXED
          EVALUATION budget (not fixed generations, which would silently favour
          large populations).

THE HONEST RESULT (asserted by ``test_honest_2opt_not_beaten_by_naive_ga``): at
equal evaluation budget, 2-opt hill climbing beats a naive GA on this 30-city
instance. A GA is a design space, not a magic wand — report what you measure.
"""
import random

from localsearch import (
    TSP, load_tsp, load_instances, validate_tour,
    one_point_crossover, two_opt_neighbors,
    tsp_hill_climb, tsp_genetic_algorithm,
)


# ---- Task 1: the two TSP genetic operators ----------------------------------

def order_crossover(parent1, parent2, rng):
    """Order crossover (OX). Returns a child that is a VALID permutation.

    1. Pick two cut points ``a <= b``.
    2. Copy ``parent1[a..b]`` straight into the child at the same positions.
    3. Fill the rest — walking from ``b+1`` and wrapping around — with the cities
       of ``parent2`` in parent2's order, skipping any already copied.
    Because step 2 takes each city once and step 3 supplies exactly the cities not
    yet taken (in a fixed order), no city repeats or goes missing.
    """
    n = len(parent1)
    a, b = sorted(rng.sample(range(n), 2))
    child = [None] * n
    child[a:b + 1] = list(parent1[a:b + 1])
    taken = set(parent1[a:b + 1])
    # parent2's cities, in order, minus the ones already copied from parent1.
    fill = [c for c in parent2 if c not in taken]
    idx = 0
    for step in range(n):
        pos = (b + 1 + step) % n            # walk from b+1, wrapping around
        if child[pos] is None:
            child[pos] = fill[idx]
            idx += 1
    return child


def swap_mutation(tour, rng):
    """Swap mutation: return a NEW tour with two positions exchanged. A swap
    cannot create a duplicate, so the result is always a valid permutation."""
    t = list(tour)
    i, j = rng.sample(range(len(t)), 2)
    t[i], t[j] = t[j], t[i]
    return t


# ---- Task 2: the hyperparameter study ---------------------------------------

SEED_BASE = 20250806


def run_study(tsp=None, n_seeds=5, max_evals=20_000):
    """Vary population (20, 50, 100) x mutation rate (0.001, 0.01, 0.1) x
    tournament (2, 5), ``n_seeds`` seeds each, at a FIXED EVALUATION budget.
    Return rows of ``(pop, mut, tourn, mean_len, std_len)``.

    Fixed *evaluations* (not generations) is the methodological rule that makes
    the comparison valid: pop=100 for 50 gens and pop=20 for 250 gens are the same
    compute, and the given driver already counts evaluations — we do not change
    that. For the crossover ablation, re-run with ``use_crossover=False``.
    """
    import numpy as np
    tsp = tsp or load_tsp()
    rows = []
    for pop in (20, 50, 100):
        for mut in (0.001, 0.01, 0.1):
            for tourn in (2, 5):
                lens = []
                for s in range(n_seeds):
                    best_len, _ = tsp_genetic_algorithm(
                        tsp, order_crossover, swap_mutation,
                        random.Random(SEED_BASE + s),
                        pop_size=pop, mutation_rate=mut, tournament=tourn,
                        max_evals=max_evals)
                    lens.append(best_len)
                rows.append((pop, mut, tourn,
                             float(np.mean(lens)), float(np.std(lens))))
    return rows


if __name__ == "__main__":
    tsp = load_tsp()
    rng = random.Random(20250806)
    nn = tsp.nearest_neighbor_tour()
    print(f"instance: {tsp.n} cities")
    print(f"  random tour        len = {tsp.length(tsp.random_tour(rng)):.1f}")
    print(f"  nearest-neighbour  len = {tsp.length(nn):.1f}")
    hc_tour, hc_len = tsp_hill_climb(tsp, random.Random(1), max_evals=20_000)
    print(f"  2-opt hill climb   len = {hc_len:.1f}")
    ga_len, _ = tsp_genetic_algorithm(
        tsp, order_crossover, swap_mutation, random.Random(1), max_evals=20_000)
    print(f"  naive GA           len = {ga_len:.1f}")
