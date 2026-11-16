"""Provided tests for the week-11 swarm studio.

Run: ``python3 test_swarm.py``. Prints one line per test. Two tests exercise the
GIVEN engine and preserve the notebook's two HONEST results verbatim -- they pass
before you write a line:

  * ``test_pso_velocity_clamping_prevents_divergence`` -- the guarantee-failing
    test. Without velocity clamping the swarm loses its ability to exploit; at an
    EQUAL evaluation budget it converges to a strictly WORSE optimum. Every year
    someone "fixes" this by removing the clamp check. Do not: the failure is the
    lesson.
  * ``test_aco_rho_matters_only_with_elitist_deposit`` -- the ρ ablation, honest.
    Under the standard (every-ant) deposit rule, evaporation ρ barely changes the
    best tour on this instance (β=2 lets greedy visibility dominate). ρ only
    becomes decisive under elitist deposit. The textbook says "evaporation is the
    algorithm"; it is true of SOME configurations and nearly irrelevant to
    others, and reporting exactly that is the point.

The other two tests call YOUR ``starter.py`` (random_search, run_bakeoff) and
fail with NotImplementedError until you implement them. Budgets are small so the
whole suite runs in a few seconds (the Session-A notebook takes ~3 min).
"""
import sys

import numpy as np

from swarm import (
    Budget, BudgetExhausted, SEED,
    rastrigin, pso, aco, tour_length, nearest_neighbour_tour,
)
import starter as s


# ---- given-engine tests (pass immediately) ----------------------------------

def test_budget_caps_evaluations_and_tracks_best():
    """The harness contract: exactly ``max_evals`` evaluations are allowed, and
    ``best`` / ``trace`` are monotone non-increasing best-so-far."""
    b = Budget(rastrigin, 50)
    for _ in range(50):
        b(np.random.default_rng(0).uniform(-5, 5, 3))
    assert b.used == 50
    try:
        b(np.zeros(3))
        raise AssertionError("Budget did not raise BudgetExhausted at the cap")
    except BudgetExhausted:
        pass
    assert b.trace == sorted(b.trace, reverse=True), "trace is not monotone best-so-far"
    assert b.best == b.trace[-1]
    print("  ok  Budget caps at max_evals and tracks a monotone best-so-far trace")


def test_pso_velocity_clamping_prevents_divergence():
    """GUARANTEE-FAILING test (honest). At an equal budget, PSO WITH velocity
    clamping finds a strictly better optimum than the same PSO without it -- the
    unclamped swarm's velocities overshoot the search box every step and it never
    settles. Remove the clamp and watch the result get worse, not better."""
    def run(clamp):
        b = Budget(rastrigin, 3000)
        pso(b, dim=10, rng=np.random.default_rng(SEED), clamp=clamp)
        return b.best
    clamped, unclamped = run(True), run(False)
    assert clamped < unclamped, (
        f"expected clamped PSO ({clamped:.3f}) to beat unclamped ({unclamped:.3f}) "
        "at equal budget. If it does not, velocity clamping was quietly disabled."
    )
    print(f"  ok  PSO needs velocity clamping: clamped {clamped:.2f} < "
          f"unclamped {unclamped:.2f} at equal budget (the honest failure)")


def test_aco_rho_matters_only_with_elitist_deposit():
    """The honest ρ ablation. Spread of best-tour length across ρ ∈ {0, 0.1, 0.5}
    is small under the standard deposit rule but large under elitist deposit --
    evaporation only bites once positive feedback exists to counterbalance."""
    def spread(elitist):
        lens = []
        for rho in (0.0, 0.1, 0.5):
            b = Budget(tour_length, 1500)
            _, L, _, _ = aco(b, rho=rho, elitist=elitist,
                             rng=np.random.default_rng(SEED))
            lens.append(L)
        return max(lens) - min(lens)
    std_spread, elit_spread = spread(False), spread(True)
    assert std_spread < 25, (
        f"standard-deposit ρ spread {std_spread:.1f} is unexpectedly large -- "
        "β=2 visibility should make ρ nearly irrelevant here."
    )
    assert elit_spread > 35 and elit_spread > std_spread, (
        f"elitist-deposit ρ spread {elit_spread:.1f} should be large (and larger "
        f"than the standard {std_spread:.1f}); ρ only matters with positive feedback."
    )
    print(f"  ok  ACO ρ matters ONLY with elitism: spread {std_spread:.1f} (standard) "
          f"vs {elit_spread:.1f} (elitist) -- the honest ablation")


def test_aco_beats_nearest_neighbour_baseline():
    """Sanity: with a real budget, ACO improves on the greedy NN tour."""
    nn_len = tour_length(nearest_neighbour_tour())
    b = Budget(tour_length, 4000)
    _, L, _, _ = aco(b, rng=np.random.default_rng(SEED))
    assert L < nn_len, f"ACO tour {L:.1f} did not beat NN baseline {nn_len:.1f}"
    print(f"  ok  ACO ({L:.1f}) beats nearest-neighbour baseline ({nn_len:.1f})")


# ---- starter tests (fail with NotImplementedError until implemented) --------

def test_random_search_respects_budget():
    """Task 1. The baseline must spend EXACTLY the budget and leave a finite best.
    Fails with NotImplementedError until you write ``random_search``."""
    b = Budget(rastrigin, 500)
    s.random_search(b, dim=5, rng=np.random.default_rng(SEED))
    assert b.used == 500, f"random_search spent {b.used} of 500 evaluations"
    assert np.isfinite(b.best), "random_search left no finite best value"
    print(f"  ok  random_search spends the whole budget (best {b.best:.2f})")


def test_bakeoff_is_fair_and_metaheuristic_beats_random():
    """Task 2. run_bakeoff returns well-formed rows AND, on Rastrigin dim 2 at
    equal budget, PSO beats the random-search baseline (if it did not, the
    comparison would not be worth running). Fails with NotImplementedError until
    both starter functions exist."""
    rows = s.run_bakeoff(n_seeds=3, evals=1200, dims=(2,))
    assert rows and all(len(r) == 4 for r in rows), "rows must be (problem, algo, mean, std)"
    assert all(np.isfinite(m) and np.isfinite(sd) for _, _, m, sd in rows)
    table = {(p, a): m for p, a, m, sd in rows}
    pso_m = table[("Rastrigin dim 2", "PSO")]
    rnd_m = table[("Rastrigin dim 2", "random")]
    assert pso_m < rnd_m, (
        f"at equal budget PSO ({pso_m:.3f}) should beat random search ({rnd_m:.3f}) "
        "on Rastrigin dim 2 -- check you gave every algorithm the SAME evals."
    )
    print(f"  ok  bake-off is fair and PSO ({pso_m:.3f}) beats random ({rnd_m:.3f}) "
          "on Rastrigin dim 2 at equal budget")


TESTS = [
    test_budget_caps_evaluations_and_tracks_best,
    test_pso_velocity_clamping_prevents_divergence,
    test_aco_rho_matters_only_with_elitist_deposit,
    test_aco_beats_nearest_neighbour_baseline,
    test_random_search_respects_budget,
    test_bakeoff_is_fair_and_metaheuristic_beats_random,
]


def main():
    failed = 0
    for t in TESTS:
        try:
            t()
        except NotImplementedError:
            print(f"  --  {t.__name__}: starter not implemented yet")
            failed += 1
        except AssertionError as e:
            print(f"  FAIL {t.__name__}: {e}")
            failed += 1
    if failed:
        print(f"\n{failed}/{len(TESTS)} failed")
        sys.exit(1)
    print(f"\nall {len(TESTS)} tests pass")


if __name__ == "__main__":
    main()
