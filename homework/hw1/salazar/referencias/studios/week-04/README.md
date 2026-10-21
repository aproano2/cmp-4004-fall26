# Week 4 Studio — Heuristics on a Weighted Grid

**Companion to** [`../../weeks/week-04.md`](../../weeks/week-04.md) — Session B.
**Time budget:** Recap 5 · Breakouts 45 · Demos 20 · Debrief 10 (80 min total).
**Deliverables:** all provided tests pass, and a scaling plot for the LLM duel.

> **Warm-up (5 min).** *Why was `h_bad` faster in the notebook? What did it cost?*

## Files in this folder

| File | Purpose | You edit it? |
|---|---|---|
| [`gridworld.py`](gridworld.py) | Given: the A* engine + weighted-grid problem, unchanged from the notebook | ❌ |
| [`instances.json`](instances.json) | Given: 40 seeded grids — 10 each at 5×5, 8×8, 12×12, 16×16 (seed 20260807) | ❌ |
| [`starter.py`](starter.py) | **Task 1** — fill in four heuristics (three admissible, one deliberately bad) | ✅ |
| [`test_heuristics.py`](test_heuristics.py) | Provided tests, incl. `test_inadmissible_heuristic_returns_suboptimal_path` | ❌ |
| [`duel.py`](duel.py) | **Task 2** — checker + scoring categories + the exact prompt from the plan | ❌ (use it) |
| [`_generate_instances.py`](_generate_instances.py) | Regenerates `instances.json` (only needed if you rotate the seed) | ❌ |

## Task 1 — Heuristics + provided tests (15 min)

Open `starter.py`. Implement:

- `h_manhattan` — plain Manhattan (admissible **here** because `MIN_COST == 1`; ask yourself when it stops being admissible)
- `h_manhattan_scaled` — Manhattan × `MIN_COST` (the correct admissible heuristic in general)
- `h_euclidean_scaled` — Euclidean × `MIN_COST` (admissible but weaker on a 4-connected grid)
- `h_bad` — **inadmissible** on purpose. Suggested form: `MAX_COST × Manhattan` (that is, `8 × Manhattan` — it overestimates a path that runs through mostly cheap cells)

Then:

```bash
python3 test_heuristics.py
```

All five tests must pass. The last one — `test_inadmissible_heuristic_returns_suboptimal_path` — is the point: it asserts that `h_bad` breaks optimality on **at least one** of the 40 instances. A test that expects *failure* is not a mistake; watching a guarantee fail *once* is how you know the guarantee is real.

Fast-finishing pairs: **If `MIN_COST` were 2 instead of 1, would plain Manhattan still be admissible? Would it be dominated by `h_manhattan_scaled`?** Be able to say why in one sentence.

## Task 2 — The duel: LLM vs. A* (25 min)

Give an LLM the same grids A* just solved. `duel.py` has the exact prompt from the plan and a checker that classifies every reply into **four categories** (do not conflate them):

1. **illegal** — path is out of bounds or non-contiguous
2. **suboptimal** — legal path but total cost > A*'s optimum
3. **wrong_cost** — legal & optimal path, but the model's self-reported cost is wrong (⚠️ this is the interesting one)
4. **correct** — all three match

**Protocol (from the plan, non-negotiable for a valid scaling curve):**

- **Four sizes:** 5×5, 8×8, 12×12, 16×16 — 10 instances each.
- Score every reply with `duel.score_llm_reply()`. Do **not** believe the model's self-reported cost — recompute with the checker.
- If you are on the manual backend, cap at **5 instances per size** and note it (scorecard axis 6).

Sketch:

```python
from aicourse.llm import LLM   # or your own local client
from duel import prompt_for, parse_reply, score_llm_reply
from gridworld import load_instances

model = LLM()  # your configured backend
bank = load_instances()
rows = []
for size in [5, 8, 12, 16]:
    for grid in bank[size]:
        reply = model.complete(prompt_for(grid))
        path, cost = parse_reply(reply)
        rows.append((size, score_llm_reply(grid, path, cost).category))
```

**Task 3 — Plot (5 min).** Optimality rate (`correct / n`) vs. grid size. Two lines: A* at 100%, LLM declining. This plot goes in Duel 1.

## Demos (20 min)

- Ask specifically for the scaling plots. The characteristic shape — A* flat, LLM cliff — is best discovered by students, then seen to *replicate* across the room. Three pairs showing the same cliff stops being anecdote.
- Solicit: *did anyone's LLM return a path shorter than A*'s optimum?* If yes, it is **illegal** or **wrong_cost** — a live debugging moment.

## Debrief (10 min)

- A* is optimal **because** of a provable property. `h_bad` shows that property fail on request.
- The LLM has no such property. Its performance is an empirical average over your distribution and it tells you nothing about instance #31.
- Anti-pattern to name and shame: **using the model as its own oracle** ("does your path look correct?"). Always validate with the checker. This is scorecard axis 3.
- **Duel 1 is live.** See [`../../projects/duel-1-search.md`](../../projects/duel-1-search.md).

## Links

- Session A notebook — [`../../notebooks/week-04-astar-heuristics.ipynb`](../../notebooks/week-04-astar-heuristics.ipynb)
- Duel 1 spec — [`../../projects/duel-1-search.md`](../../projects/duel-1-search.md)
- Duel scorecard — [`../../resources/duel-scorecard.md`](../../resources/duel-scorecard.md)
- AI policy (`AI_LOG.md`) — [`../../resources/ai-policy.md`](../../resources/ai-policy.md)
