# Homework 3 — Optimization

**Assigned:** Week 11 · **Due:** Week 12

---

## The task

Metaheuristics are easy to implement and easy to compare *badly*. Most published
comparisons in this literature are methodologically weak — variable budgets, single
seeds, no baselines. This duel is about doing it properly.

## Requirements

### Part 1 — Implement

At least **three** of: GA, simulated annealing, PSO, ACO, ABC. At least one must be
written from scratch by you (not adapted from starter code).

Two problem classes:

- **Continuous:** Rastrigin and Rosenbrock, at dimensions 2, 10, and 30
- **Combinatorial:** TSP at 20, 30, and 50 cities, *or* knapsack at 3 sizes

### Part 2 — Compare fairly

This is where the marks are.

**Non-negotiable protocol:**

1. **Equal evaluation budget.** Every algorithm gets exactly the same number of
   objective-function evaluations. Not equal iterations, not equal generations, not
   equal wall-clock. Use the `Budget` wrapper from week 11 and report the cap.
2. **≥ 10 seeds per configuration.** Report mean ± std, or median with IQR. A
   stochastic algorithm reported from one run is not a result.
3. **Convergence plots with x-axis = evaluations**, with error bands across seeds.
4. **Two mandatory baselines**, because metaheuristics look impressive until you
   check them against something dumb:
   - **Random search** at the same budget
   - A **problem-specific heuristic**: nearest-neighbour + 2-opt for TSP, greedy
     ratio for knapsack, or plain hill climbing with restarts for continuous

If random search is competitive with your metaheuristic, **report that
prominently.** It happens more often than the literature suggests and finding it is
a better outcome than hiding it.

**A hyperparameter study on one algorithm.** Grid over at least two parameters,
5 seeds each, reported as a table and a heatmap. State which parameters mattered
and which did not.

### Part 3 — The LLM arm

Pick **one**, and justify the choice:

**Option A — LLM as mutation operator (FunSearch-style).** The model proposes
*code* for a heuristic; your sound evaluator scores it; best candidates seed the
next round. Compare against a GA over numeric parameters at equal budget — and
**define carefully what "equal budget" means here**, since one LLM call is not one
function evaluation. Your definition and its defense are part of the grade.

**Option B — LLM as hyperparameter tuner.** Give the model your algorithm's
convergence history and let it propose the next configuration. Compare against
random search and grid search over the same number of configurations.

**Option C — LLM as direct optimizer.** Give it the problem and ask for a
solution. Cheap to run and expected to perform poorly; if you choose this, you must
also do A or B, since C alone is not enough content.

Required for whichever you choose:

- **Compile/crash rate** of model-generated code (option A) — report it, do not
  quietly discard failures
- Cost accounting in tokens and wall-clock
- **Interpretability assessment:** can you read the best evolved heuristic and
  explain *why* it works? This is the axis where the LLM approach genuinely wins
  over a tuned parameter vector, and it deserves a real paragraph.

### Part 4 — Report 

```
homework/hw3/{lastname}
├── REPORT.md              ≤ 2 500 words
├── code/
├── results/*.csv          all seeds, all configs — raw
├── fig/*.png              ≥ 4 figures
├── .llm_cache/
└── AI_LOG.md
```

Must include:

1. **Duel Scorecard**
2. Convergence plots with error bands, x-axis = evaluations
3. The hyperparameter heatmap
4. A **No Free Lunch statement**: name which algorithm suited which problem
   structure, and say why in terms of the problem's properties (multimodality,
   separability, discreteness) rather than in terms of the biological metaphor
5. **"Where we may have been unfair"** — in this duel, address specifically:
   equal-budget definition, whether you tuned one algorithm more than another,
   whether your baselines were given a fair shot
6. A closing paragraph on **whether the biological metaphors earned their keep**.
   You have the data. Did the ant-inspired algorithm beat the bee-inspired one for
   reasons connected to ants and bees, or for reasons connected to memory
   structure? Defend your answer.

