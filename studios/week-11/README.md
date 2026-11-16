# Week 11 Studio — Swarm Intelligence: The Budget-Normalized Bake-Off

**Companion to** [`../../weeks/week-11.md`](../../weeks/week-11.md) — Session B.
**Time budget:** Recap 5 · Breakouts 45 · Demos 20 · Debrief 10 (80 min total).
**Deliverables:** all provided tests pass; a mean ± std bake-off table, one
convergence plot with error bands (x-axis = **evaluations**), and a one-line
which-algorithm-suits-which-structure statement backed by your data.

> **Duel 3 (Optimization) is due this week** — collected in Session A. This studio
> is its methodological rehearsal: the `Budget` harness here is *the same wrapper*
> Duel 3 requires, and the fair-comparison protocol you build in `starter.py`
> (equal evaluations, ≥ 10 seeds, a random-search baseline) is exactly the 30 %
> the duel grades hardest. Spec: [`../../projects/duel-3-optimization.md`](../../projects/duel-3-optimization.md).

> **Recap (5 min).** *Why is comparing metaheuristics at equal iterations unfair?
> What is the right axis?* (A GA with population 100 spends 100 evaluations per
> generation; PSO with 30 particles spends 30. Equal *iterations* silently hands
> compute to whoever has the bigger population. Equal **evaluations** is the only
> defensible axis — and `Budget` is what enforces it.)

## Files in this folder

| File | Purpose | You edit it? |
|---|---|---|
| [`swarm.py`](swarm.py) | Given: the `Budget` harness + Rastrigin/Rosenbrock + the seeded TSP + **PSO, ACO, ABC** — all extracted verbatim from the Session-A notebook | ❌ |
| [`instances.json`](instances.json) | Given: the 25-city TSP instance + its nearest-neighbour known-good tour (seed 20250806) | ❌ |
| [`starter.py`](starter.py) | **Task 1** — `random_search` (the baseline); **Task 2** — `run_bakeoff` (the equal-budget study) | ✅ |
| [`test_swarm.py`](test_swarm.py) | Provided tests, incl. the two honest results below | ❌ |
| [`_generate_instances.py`](_generate_instances.py) | Re-records `instances.json` (only needed if you rotate the seed) | ❌ |

> **On the given code.** PSO, ACO, and ABC are provided so you spend the studio on
> *comparison*, not re-implementation. `Budget` is the fair-comparison harness —
> it is **given, not a TODO**. (For Duel 3, each pair implements one algorithm
> from scratch; here you drive the provided three.)

## Task 1 — The random-search baseline (10 min)

Open `starter.py` and implement `random_search(budget, dim, bounds, rng)`: sample
uniform points and evaluate them through `budget` until it is exhausted. Trivial —
and that is the point. Metaheuristics look impressive *until you check them against
something dumb*. If random search is competitive with your swarm at equal budget,
**report that prominently**; it happens more often than the literature admits, and
finding it is a better outcome than hiding it.

```bash
python3 test_swarm.py
```

`test_random_search_respects_budget` asserts the baseline spends *exactly* the
budget — the same evaluation accounting every algorithm is held to.

## Task 2 — The bake-off, done honestly (25 min)

Fill in `run_bakeoff()`. For Rastrigin and Rosenbrock at each dimension, run **PSO,
ABC, and random search** for **≥ 10 seeds each**, every run on a fresh
`Budget(func, evals)` with the **same `evals`**. Return `(problem, algo, mean, std)`
rows.

> **The rule that makes it valid:** fixed *evaluations*, not fixed *iterations* or
> *wall-clock*. `Budget` counts evaluations for you; give every algorithm the same
> cap and never "fix" it to count generations. This is the week-10 fixed-budget
> rule, generalized across algorithm families.

Deliverables built on the returned rows:

- **Table:** mean ± std of best value found, per problem × algorithm.
- **One convergence plot** with error bands, **x-axis = evaluations** (use
  `budget.trace`, which is indexed by evaluation). Not iterations. Ever.
- **Which suits which:** one line per problem naming the winner *and* the reason in
  terms of problem structure (multimodality, separability, dimensionality) — not
  the biological metaphor. Expect PSO strong on continuous problems, ABC's scout
  restarts helping on the highly multimodal Rastrigin, and **no algorithm winning
  everywhere**. That last one is the No Free Lunch theorem showing up in your own
  data; name it when it appears.

`test_bakeoff_is_fair_and_metaheuristic_beats_random` checks the rows are
well-formed and that PSO beats random search on Rastrigin dim 2 — if it did not,
the comparison would not be worth running.

## The two honest results (given-code tests — do not "tidy" them)

Both pass before you write a line, and both are lifted verbatim from the notebook's
honest ablations. **They are load-bearing, not decoration.**

- **`test_pso_velocity_clamping_prevents_divergence`** — the guarantee-failing
  test. At equal budget, PSO *with* velocity clamping finds a strictly better
  optimum than the same PSO without it. Remove the clamp (`clamp=False`) and the
  velocities overshoot the search box every step; the swarm never settles and the
  result gets **worse**. A test that expects the un-clamped version to lose is not
  a bug — watching the guarantee fail on request is how you know it was real.
- **`test_aco_rho_matters_only_with_elitist_deposit`** — the ρ ablation, kept
  honest. The textbook line is "evaporation *is* the algorithm." On *this* instance
  under the standard (every-ant) deposit rule, ρ barely moves the best tour,
  because β = 2 lets the greedy visibility term dominate. ρ only becomes decisive
  under **elitist** deposit, which creates the positive feedback loop evaporation
  exists to counterbalance. Two lessons, the second the one that transfers: (1) a
  parameter's importance depends on the rest of the configuration; (2) the notebook
  author *changed the experiment* to make the effect visible — which is legitimate
  **only because they said so**. Silently reporting the one config that shows what
  you expected is the single most common flaw in the literature this week critiques.

## Task 3 — Failure Atlas + notes (5 min)

Add today's entries: the equal-iterations-vs-equal-evaluations trap, PSO divergence
without velocity clamping, ACO's ρ that only bites under elitist deposit, and
whether random search was competitive with any swarm on any problem.

## Demos (20 min)

Two pairs: one bake-off table, one convergence plot. If any pair reports a
single-run number without variance, rerun their config live with a different seed
and show the number move — a stochastic algorithm reported from one run is an
anecdote, not a result. Ask specifically: *did random search beat any swarm
anywhere?*

## Debrief (10 min)

- The four metaheuristics share one skeleton and differ in **what they remember**
  (population / `p_best`+`g_best` / pheromone matrix / trial counters). The
  metaphors are pedagogy, not mechanism.
- Fair comparison requires **budget normalization**. Most published metaheuristic
  comparisons are weaker than what you just did — say so; it is true and it builds
  justified confidence.
- No Free Lunch is not a slogan here; it is in your table. Attribute wins to
  problem *structure*, never to ants or bees.
- **The FunSearch arm (Task 2 of the lesson's Session B) lives in Duel 3**, where
  you have the compute budget and word count to do it honestly — including the
  compile/crash rate of model-generated code. Its architecture (unreliable
  generator, sound evaluator) is week 9's LLM-Modulo pattern, third instance.
- Week 12 changes subject: from optimization to reasoning under uncertainty.

## Links

- Session A notebook — [`../../notebooks/week-11-swarm-intelligence.ipynb`](../../notebooks/week-11-swarm-intelligence.ipynb)
- Lesson plan — [`../../weeks/week-11.md`](../../weeks/week-11.md)
- Slides — [`../../slides/week-11/deck.md`](../../slides/week-11/deck.md)
- Duel 3 spec — [`../../projects/duel-3-optimization.md`](../../projects/duel-3-optimization.md)
- Duel scorecard — [`../../resources/duel-scorecard.md`](../../resources/duel-scorecard.md)
- AI policy (`AI_LOG.md`) — [`../../resources/ai-policy.md`](../../resources/ai-policy.md)
