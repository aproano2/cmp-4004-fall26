"""Week 11 studio — starter (the fair-comparison harness).

The three metaheuristics (PSO, ACO, ABC) are GIVEN in ``swarm.py``. What you
build here is the thing the week is actually about: an HONEST comparison.

  Task 1  random_search()  -- the mandatory "dumb" baseline. Metaheuristics look
                              impressive until you check them against random
                              sampling at the same budget. Sometimes random wins;
                              finding that out is a better result than hiding it.
  Task 2  run_bakeoff()     -- multi-seed, EQUAL-EVALUATION-BUDGET study returning
                              mean ± std per (problem, algorithm). This is the
                              protocol Duel 3 grades at 30%.

Run ``python3 test_swarm.py`` as you go. The two given-code tests
(PSO clamping, ACO ρ-vs-elitism) pass immediately; the two that call YOUR code
fail with NotImplementedError until you fill these in.

THE METHODOLOGICAL RULE that makes any of this valid: compare at equal
EVALUATIONS, never equal iterations. ``Budget`` counts evaluations for you; feed
every algorithm a fresh ``Budget(func, evals)`` with the SAME ``evals``.
"""
import numpy as np

from swarm import (
    Budget, BudgetExhausted, SEED,
    rastrigin, rosenbrock, pso, abc_optimize,
)


# ---- Task 1: the random-search baseline -------------------------------------

def random_search(budget, dim, bounds=(-5.12, 5.12), rng=None):
    """Uniformly sample points in ``bounds`` and evaluate them through ``budget``
    until the budget is exhausted. No memory, no learning -- the honest control.

    Recipe:
      1. ``rng = rng or np.random.default_rng(SEED)``; ``lo, hi = bounds``.
      2. While ``not budget.exhausted()``: draw ``rng.uniform(lo, hi, dim)`` and
         pass it to ``budget(...)`` inside a try/except BudgetExhausted (break on
         exhaustion). ``budget.best`` tracks the best value for you -- you need
         not return anything, but returning the best point found is fine.
    """
    # TODO: sample-and-evaluate until the budget is spent.
    raise NotImplementedError


# ---- Task 2: the equal-budget, multi-seed bake-off --------------------------

def run_bakeoff(n_seeds=10, evals=6000, dims=(2, 10, 30)):
    """The fair comparison (plan §11B, Task 1). For each continuous problem
    (Rastrigin, Rosenbrock) at each dimension in ``dims``, run PSO, ABC, and the
    random-search baseline for ``n_seeds`` seeds, each on a FRESH
    ``Budget(func, evals)`` -- i.e. the SAME evaluation budget for every
    algorithm. Return a list of rows ``(problem, algo, mean, std)`` where
    ``problem`` is e.g. ``"Rastrigin dim 10"`` and mean/std are over the seeds'
    best values found.

    Seed discipline: use ``np.random.default_rng(SEED + s)`` for seed ``s`` so
    every algorithm sees the same seed sequence.

    Deliverables built ON TOP of these rows (see README): the mean ± std table,
    a convergence plot with error bands (use ``budget.trace``, x-axis =
    EVALUATIONS), and a one-line statement of which algorithm suits which problem
    structure -- and whether either beats random search at all.
    """
    algos = [
        ("PSO",    lambda b, d, r: pso(b, dim=d, rng=r)),
        ("ABC",    lambda b, d, r: abc_optimize(b, dim=d, rng=r)),
        ("random", lambda b, d, r: random_search(b, dim=d, rng=r)),
    ]
    problems = [("Rastrigin", rastrigin), ("Rosenbrock", rosenbrock)]
    rows = []
    for pname, func in problems:
        for dim in dims:
            for aname, runner in algos:
                # TODO: for s in range(n_seeds): make a fresh Budget(func, evals),
                # run ``runner(budget, dim, np.random.default_rng(SEED + s))``
                # inside try/except BudgetExhausted, collect ``budget.best``.
                # Then append (f"{pname} dim {dim}", aname, mean, std) using
                # np.mean / np.std over the collected bests.
                raise NotImplementedError
    return rows


if __name__ == "__main__":
    # Smoke test: one seed each on Rastrigin dim 2, small budget.
    for name, run in [("PSO",    lambda b: pso(b, dim=2, rng=np.random.default_rng(0))),
                      ("ABC",    lambda b: abc_optimize(b, dim=2, rng=np.random.default_rng(0))),
                      ("random", lambda b: random_search(b, dim=2, rng=np.random.default_rng(0)))]:
        b = Budget(rastrigin, 2000)
        try:
            run(b)
            print(f"  {name:>7}: best = {b.best:.4f}")
        except NotImplementedError:
            print(f"  {name:>7}: -- not implemented yet")
