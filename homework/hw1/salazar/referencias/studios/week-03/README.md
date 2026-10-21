# Week 3 Studio — One Search Function, Four Algorithms

**Companion to** [`../../weeks/week-03.md`](../../weeks/week-03.md) — Session 3B.
**Time budget:** Recap 5 · Breakouts 45 · Demos 20 · Debrief 10 (80 min total).
**Deliverables:** all provided tests pass, a defensible problem formulation, and a
log-scale scaling plot.

> **Recap (5 min).** *Why does the goal test go on **expansion**, not generation?*
> Cold-call. If nobody has it, re-draw the 3-node graph (`TinyGraph` in `search.py`):
> `start→A` costs 10, `start→B→A` costs 2. Testing at generation returns 10.

## Files in this folder

| File | Purpose | You edit it? |
|---|---|---|
| [`search.py`](search.py) | Given: `Problem`, `Node`, `Frontier`, the generic `search()`, and the `EightPuzzle` / `TinyGraph` fixtures — unchanged from the notebook | ❌ |
| [`instances.json`](instances.json) | Given: 40 8-puzzle instances — 10 each at optimal depths 4, 8, 12, 16 (seed 20260807; depths verified by exhaustive BFS) | ❌ |
| [`starter.py`](starter.py) | **Tasks 1–3** — formulate M&C, implement the four algorithms, measure | ✅ |
| [`test_search.py`](test_search.py) | Provided tests, incl. `test_bfs_suboptimal_nonuniform_cost` | ❌ |
| [`_generate_instances.py`](_generate_instances.py) | Regenerates `instances.json` (only if you rotate the seed) | ❌ |

The `search()` interface here is the course's **most reused artifact**: week 4's
A\* is a 10-line diff on it, and week 9's planner imports it unchanged. Get it
right and the next weeks are much faster.

## Task 1 — Formulate missionaries & cannibals (10 min)

Open `starter.py` and fill in `MissionariesAndCannibals(Problem)`: initial state,
`actions`, `result`, and `is_goal`. **No searching yet** — this is the five-component
formulation from the slides, as code.

Three missionaries, three cannibals, one boat carrying 1 or 2 (never empty). If
cannibals ever **outnumber** missionaries on *either* bank — including the bank the
boat just left — the missionaries are eaten. Get everyone across.

Two things surface every year, and both are the point:

1. The constraint applies to **both** banks, *including the one you just left*.
2. Do you exclude illegal states in `actions()` or in `result()`? **Both are
   legitimate designs.** Pick one and be ready to *defend* it in the demo — that
   argument is the week's real skill. *Half of applied AI is choosing a good
   representation before you write any algorithm.*

Formulation is graded, not just the code.

## Task 2 — Implement all four (25 min)

Still in `starter.py`. Fill in `bfs`, `dfs`, `ucs`, and `ids`.

Three of them are **one line each** — that is the insight of the week. BFS, DFS,
and UCS are the *same* `search()` loop with a different frontier discipline:

| Algorithm | `frontier_kind` | Complete? | Optimal? | Space |
|---|---|---|---|---|
| BFS | `"fifo"` | Yes | Uniform costs **only** | O(b^d) |
| DFS | `"lifo"` | Finite spaces w/ cycle control | No | O(bm) |
| UCS | `"priority"` | Yes | **Yes** (non-neg. costs) | O(b^(1+⌊C\*/ε⌋)) |
| IDS | depth-limited, iterated | Yes | Uniform costs only | **O(bd)** |

`ids` is the interesting one and does **not** call `search()`. Write a recursive
`depth_limited(problem, limit)` that returns `(node, expansions, hit_limit)`, then
iterate the limit from 0 upward. IDS buys BFS's completeness at DFS's memory cost
by re-doing the shallow work — and the redundancy is a *constant factor*, not an
exponential one (≈11 % at b≈10). Cheap.

Then run:

```bash
python3 test_search.py
```

All five must pass. The one to read carefully is
`test_bfs_suboptimal_nonuniform_cost` — **it asserts BFS returns the wrong (cost-10)
path** on `TinyGraph`. That is not a broken test. BFS's optimality claim has a
condition (uniform step costs); this instance violates it. A guarantee you cannot
watch fail is a guarantee you have not understood. The other four:

- `test_bfs_optimal_uniform_cost` — on the 8-puzzle (every move costs 1), BFS *is* optimal.
- `test_dfs_terminates_on_cyclic_graph` — DFS on a 3-cycle **terminates** only
  because `search()` keeps an explored set. Delete it and this hangs.
- `test_ucs_optimal_nonuniform_cost` — UCS returns the cost-2 path `TinyGraph`. This
  is *why UCS exists*.
- `test_ids_matches_bfs_solution_length` — IDS finds the same-length solution as BFS
  at O(bd) memory.

## Task 3 — Measure (10 min)

Run all four on the provided 8-puzzle bank — depths 4, 8, 12, 16, ten instances
each. `starter.measure()` gives you the loop. Produce:

- **Table:** expansions, solution length (add max frontier size / wall-clock if you like).
- **Plot:** expansions vs. depth, **log y-axis**.

The log-scale plot is *the* deliverable. Straight lines on a log axis mean
exponential growth — and seeing it in your own data is what makes the warm-up poll
finally land. Never write a search without the `expansions` counter: it is the only
currency in which these four can be compared (scorecard axis 3).

## Demos (20 min)

Two pairs. One presents the **formulation disagreement** from Task 1 (`actions()`
vs. `result()` — make them defend it). One presents the **scaling plot**. For the
plot, ask: *extrapolate to depth 24 — is your laptop enough?* (No. And that is why
week 4 exists.)

## Debrief (10 min)

- Uninformed search is **complete but blind**. Every guarantee we have costs
  exponential resources.
- DFS *found* a goal on the deep instances — a terrible one, hundreds of moves long.
  Optimality is not a nice-to-have you can eyeball.
- **No LLM comparison this week, deliberately:** you cannot evaluate a competitor
  until you can measure the incumbent. Week 4 is the first duel.
- Keep this code. Next week adds one thing — a heuristic — and A\* is a 10-line diff.

> **Failure Atlas entry due.** Classical failures count: an exponential blowup is a
> failure worth documenting.

## Links

- Session 3A notebook — [`../../notebooks/week-03-uninformed-search.ipynb`](../../notebooks/week-03-uninformed-search.ipynb)
- Week 4 studio (A\* on top of this interface) — [`../week-04/`](../week-04/)
- Duel 1 spec (uses this `search()`) — [`../../projects/duel-1-search.md`](../../projects/duel-1-search.md)
- AI policy (`AI_LOG.md`) — [`../../resources/ai-policy.md`](../../resources/ai-policy.md)
