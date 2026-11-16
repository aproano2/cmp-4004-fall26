"""Week 11 studio — the swarm engine (GIVEN; do not modify).

Session B is a *budget-normalized bake-off* across metaheuristics. This file
provides everything you are NOT asked to write, extracted VERBATIM from the
Session-A notebook (``week-11-swarm-intelligence.ipynb``, same seed):

  * the ``Budget`` harness — the whole point of the week. Every algorithm gets
    exactly the same number of fitness EVALUATIONS. Comparing at equal
    *iterations* is meaningless (a GA with population 100 spends 100 evals per
    generation; PSO with 30 particles spends 30). Equal evaluations is the only
    defensible axis, and ``Budget`` is what enforces it. It is GIVEN, not a TODO.
  * two continuous benchmarks: ``rastrigin`` (highly multimodal) and
    ``rosenbrock`` (a curved valley), global minimum 0 for both.
  * a seeded TSP instance (``make_tsp``) + ``tour_length`` +
    ``nearest_neighbour_tour`` (the greedy "known-good" baseline).
  * three metaheuristics, verbatim: ``pso``, ``aco``, ``abc_optimize``.

You implement the fair-comparison harness in ``starter.py``: the random-search
baseline and the multi-seed, equal-budget bake-off that calls these algorithms.

⚠️ Two honest results are baked into this code and its tests — do NOT "tidy" them:
  * PSO needs velocity clamping. Turn ``clamp=False`` and the swarm loses its
    ability to exploit (velocities overshoot the box every step); at equal budget
    it finds a strictly worse optimum. ``test_swarm.py`` asserts this.
  * ACO's evaporation ρ *barely matters* under the standard (every-ant) deposit
    rule on this instance, because β=2 lets greedy visibility dominate. ρ only
    becomes decisive under ``elitist=True`` deposit, which creates the positive
    feedback loop evaporation exists to counterbalance. This is the notebook's
    honest ablation; ``test_swarm.py`` asserts the effect appears ONLY with
    elitism. See the docstring of ``aco``.
"""
import json
import math
from pathlib import Path

import numpy as np

SEED = 20250806          # the notebook's seed — reused so results reproduce


# =============================================================================
# 1 · The budget harness — the fair-comparison rule that governs the studio
# =============================================================================

class BudgetExhausted(Exception):
    pass


class Budget:
    """Every algorithm gets exactly the same number of fitness evaluations."""

    def __init__(self, f, max_evals):
        self.f, self.max_evals, self.used = f, max_evals, 0
        self.best = float("inf")
        self.trace = []          # best-so-far, indexed by EVALUATION

    def __call__(self, x):
        if self.used >= self.max_evals:
            raise BudgetExhausted()
        self.used += 1
        v = self.f(x)
        self.best = min(self.best, v)
        self.trace.append(self.best)
        return v

    def exhausted(self):
        return self.used >= self.max_evals


# =============================================================================
# 2 · Continuous benchmarks
# =============================================================================

def rastrigin(x):
    x = np.asarray(x)
    return 10 * len(x) + np.sum(x**2 - 10 * np.cos(2 * np.pi * x))


def rosenbrock(x):
    x = np.asarray(x)
    return np.sum(100 * (x[1:] - x[:-1]**2)**2 + (1 - x[:-1])**2)


# =============================================================================
# 3 · Particle Swarm Optimization (Kennedy & Eberhart, 1995)
#     v ← w·v + c1·φ1·(p_best − x) + c2·φ2·(g_best − x);  x ← x + v
# =============================================================================

def pso(budget, dim, bounds=(-5.12, 5.12), n=30, w=(0.9, 0.4),
        c1=1.5, c2=1.5, rng=None, clamp=True, iters_hint=None):
    rng = rng or np.random.default_rng(SEED)
    lo, hi = bounds
    x = rng.uniform(lo, hi, (n, dim))
    v = rng.uniform(-1, 1, (n, dim))
    v_max = 0.2 * (hi - lo)

    try:
        p_val = np.array([budget(xi) for xi in x])
    except BudgetExhausted:
        return None
    p_best = x.copy()
    g_best = p_best[p_val.argmin()].copy()
    g_val = p_val.min()

    total = iters_hint or max(1, budget.max_evals // n)
    t = 0
    while not budget.exhausted():
        frac = min(1.0, t / total)
        wt = w[0] + (w[1] - w[0]) * frac          # linearly decreasing inertia
        r1, r2 = rng.random((n, dim)), rng.random((n, dim))
        v = wt * v + c1 * r1 * (p_best - x) + c2 * r2 * (g_best - x)
        if clamp:
            v = np.clip(v, -v_max, v_max)          # clamping matters (see tests)
        x = np.clip(x + v, lo, hi)
        try:
            vals = np.array([budget(xi) for xi in x])
        except BudgetExhausted:
            break
        better = vals < p_val
        p_best[better], p_val[better] = x[better], vals[better]
        if p_val.min() < g_val:
            g_val = p_val.min()
            g_best = p_best[p_val.argmin()].copy()
        t += 1
    return g_best


# =============================================================================
# 4 · The studio TSP instance
# =============================================================================

def make_tsp(n_cities=25, seed=SEED):
    """Seeded Euclidean TSP: uniform points in a 100×100 square. Reproducible."""
    rng = np.random.default_rng(seed)
    pts = rng.uniform(0, 100, (n_cities, 2))
    D = np.linalg.norm(pts[:, None, :] - pts[None, :, :], axis=-1)
    np.fill_diagonal(D, 1e-9)
    return pts, D


PTS, DIST = make_tsp()               # the verbatim notebook instance (seed SEED)
NC = len(PTS)


def tour_length(tour):
    return sum(DIST[tour[i], tour[(i + 1) % len(tour)]] for i in range(len(tour)))


def nearest_neighbour_tour(start=0):
    """Greedy 'known-good' baseline: always hop to the nearest unvisited city."""
    unvisited = set(range(NC)) - {start}
    tour = [start]
    while unvisited:
        nxt = min(unvisited, key=lambda j: DIST[tour[-1], j])
        tour.append(nxt); unvisited.discard(nxt)
    return tour


# =============================================================================
# 5 · Ant Colony Optimization on TSP (Dorigo, 1996)
#     P(i→j) = [τ]^α·[η]^β / Σ[τ]^α·[η]^β;  τ ← (1−ρ)·τ + Σ Δτ
# =============================================================================

def aco(budget, n_ants=20, alpha=1.0, beta=2.0, rho=0.1, Q=100.0,
        rng=None, snapshots=None, elitist=False):
    """Returns (best_tour, best_len, snapshots, stats).

    elitist=True: only the best-so-far ant deposits. This creates the strong
    positive feedback loop that evaporation has to counterbalance -- see the
    rho ablation in the notebook (and ``test_aco_rho_matters_only_with_elitist``)
    for why that matters. Under the standard rule (every ant deposits) on this
    instance, ρ barely changes the best tour: β=2 lets greedy visibility dominate.
    """
    rng = rng or np.random.default_rng(SEED)
    tau = np.ones((NC, NC))
    eta = 1.0 / DIST
    best_tour, best_len = None, float("inf")
    snaps = []
    stats = {"colony_mean": [], "distinct_edges": []}

    while not budget.exhausted():
        tours = []
        for _ in range(n_ants):
            start = int(rng.integers(NC))
            tour = [start]
            unvisited = set(range(NC)) - {start}
            while unvisited:
                i = tour[-1]
                cand = np.fromiter(unvisited, int)
                wts = (tau[i, cand] ** alpha) * (eta[i, cand] ** beta)
                total = wts.sum()
                probs = wts / total if total > 0 else np.ones(len(cand)) / len(cand)
                j = int(rng.choice(cand, p=probs))
                tour.append(j); unvisited.discard(j)
            try:
                L = budget(tour)
            except BudgetExhausted:
                if best_tour is None:
                    best_tour, best_len = tour, tour_length(tour)
                return best_tour, best_len, snaps, stats
            tours.append((tour, L))
            if L < best_len:
                best_tour, best_len = tour, L

        # Track what the WHOLE COLONY is doing, not just the luckiest ant.
        stats["colony_mean"].append(float(np.mean([L for _, L in tours])))
        edges = set()
        for tour, _ in tours:
            for k in range(len(tour)):
                edges.add(frozenset((tour[k], tour[(k + 1) % len(tour)])))
        stats["distinct_edges"].append(len(edges))

        tau *= (1.0 - rho)                          # EVAPORATION
        depositors = [(best_tour, best_len)] if elitist else tours
        for tour, L in depositors:
            dep = Q / L
            for k in range(len(tour)):
                a, b_ = tour[k], tour[(k + 1) % len(tour)]
                tau[a, b_] += dep
                tau[b_, a] += dep
        if snapshots is not None and len(snaps) < snapshots:
            snaps.append(tau.copy())

    return best_tour, best_len, snaps, stats


# =============================================================================
# 6 · Artificial Bee Colony (Karaboga, 2007). Employed bees exploit · onlookers
#     choose by quality · scouts ABANDON a source after ``limit`` failed
#     improvements — an explicit, per-candidate restart trigger.
# =============================================================================

def abc_optimize(budget, dim, bounds=(-5.12, 5.12), n_sources=20, limit=40,
                 rng=None):
    rng = rng or np.random.default_rng(SEED)
    lo, hi = bounds
    X = rng.uniform(lo, hi, (n_sources, dim))
    try:
        fx = np.array([budget(x) for x in X])
    except BudgetExhausted:
        return None
    trials = np.zeros(n_sources, dtype=int)
    best_x, best_f = X[fx.argmin()].copy(), fx.min()

    def fitness(f):
        return 1.0 / (1.0 + f) if f >= 0 else 1.0 + abs(f)

    while not budget.exhausted():
        # --- employed bees ------------------------------------------------
        for i in range(n_sources):
            if budget.exhausted():
                break
            k = rng.integers(n_sources)
            while k == i and n_sources > 1:
                k = rng.integers(n_sources)
            j = rng.integers(dim)
            cand = X[i].copy()
            cand[j] = np.clip(X[i, j] + rng.uniform(-1, 1) * (X[i, j] - X[k, j]),
                              lo, hi)
            try:
                fc = budget(cand)
            except BudgetExhausted:
                break
            if fc < fx[i]:
                X[i], fx[i], trials[i] = cand, fc, 0
            else:
                trials[i] += 1

        # --- onlooker bees: choose proportionally to quality --------------
        fit = np.array([fitness(f) for f in fx])
        probs = fit / fit.sum() if fit.sum() > 0 else np.ones(n_sources) / n_sources
        for _ in range(n_sources):
            if budget.exhausted():
                break
            i = int(rng.choice(n_sources, p=probs))
            k = rng.integers(n_sources)
            j = rng.integers(dim)
            cand = X[i].copy()
            cand[j] = np.clip(X[i, j] + rng.uniform(-1, 1) * (X[i, j] - X[k, j]),
                              lo, hi)
            try:
                fc = budget(cand)
            except BudgetExhausted:
                break
            if fc < fx[i]:
                X[i], fx[i], trials[i] = cand, fc, 0
            else:
                trials[i] += 1

        # --- scout bees: ABANDON exhausted sources ------------------------
        worst = int(trials.argmax())
        if trials[worst] > limit and not budget.exhausted():
            X[worst] = rng.uniform(lo, hi, dim)
            try:
                fx[worst] = budget(X[worst])
            except BudgetExhausted:
                break
            trials[worst] = 0

        if fx.min() < best_f:
            best_f, best_x = fx.min(), X[fx.argmin()].copy()

    return best_x


# =============================================================================
# instance loading (documentation / known-good baseline for the TSP)
# =============================================================================

def load_instances(path=None):
    """Load the recorded TSP instance from instances.json: the seeded cities plus
    the nearest-neighbour known-good tour and its length. The live ``PTS``/``DIST``
    above are the source of truth (verbatim ``make_tsp``); this file is the
    committed snapshot students inspect (see ``_generate_instances.py``)."""
    path = Path(path or Path(__file__).with_name("instances.json"))
    return json.loads(path.read_text())


if __name__ == "__main__":
    # Smoke test the engine (does not need starter.py).
    nn = nearest_neighbour_tour()
    print(f"TSP instance: {NC} cities (seed {SEED})")
    print(f"nearest-neighbour tour length: {tour_length(nn):.1f}")

    b = Budget(rastrigin, 6000)
    pso(b, dim=10, rng=np.random.default_rng(SEED))
    print(f"PSO on Rastrigin (dim 10): best = {b.best:.4f} after {b.used} evals")

    b = Budget(tour_length, 4000)
    _, L, _, _ = aco(b, rng=np.random.default_rng(SEED))
    print(f"ACO best tour: {L:.1f}   (NN baseline {tour_length(nn):.1f})")

    b = Budget(rastrigin, 6000)
    abc_optimize(b, dim=10, rng=np.random.default_rng(SEED))
    print(f"ABC on Rastrigin (dim 10): {b.best:.4f}")
