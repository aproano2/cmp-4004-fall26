# Duel 1 — Search

**Assigned:** Week 5 · **Due:** Week 7, Monday · **Weight:** 15 %
**Team size:** Same groups as studio work

---

## The task

You have implemented BFS, DFS, UCS, IDS, and A*. Now establish, with evidence,
how they compare to each other and to a language model on the same problems.

## Deliverables

```
homework/hw1/student_lastname
├── REPORT.md              ≤ 2 000 words
├── code/                  your implementations + benchmark harness
├── results/*.csv          raw measurements
├── fig/*.png              at least 3 figures
├── .llm_cache/            your LLM transcripts (committed)
└── AI_LOG.md              per resources/ai-policy.md
```

## Part 1 — Classical comparison (40 %)

Two domains: **8-puzzle** and **weighted grid pathfinding** (terrain costs).

Required measurements, per algorithm per domain:

- Solution cost and solution length
- Node expansions
- Maximum frontier size
- Wall-clock time

Required protocol:

- **Four difficulty levels** per domain (8-puzzle: solution depths 4, 8, 12, 16;
  grids: 5×5, 8×8, 12×12, 16×16)
- **Ten instances per level.** Report medians and IQRs, not single runs.
- A hard timeout, stated. Report timeouts as timeouts, not as failures to solve.

Required analysis:

1. Verify empirically that UCS and A*-with-admissible-h return equal-cost
   solutions, and that BFS does **not** on non-uniform costs. Show the instance
   where BFS is suboptimal.
2. Demonstrate **heuristic dominance**: show that Manhattan expands no more nodes
   than misplaced-tiles on every instance. If you find a counterexample, that is a
   bug in one of your heuristics — find it.
3. Break admissibility (use `h × 3`). Report the speedup *and* the cost in
   solution quality. Both numbers, or the analysis is incomplete.
4. Compute the **effective branching factor b\*** for A* with each heuristic.

## Part 2 — The duel (40 %)

Same instances, given to a language model as text. Your choice of backend
(local model, manual transcript, or your own API access — see
[`resources/setup.md`](../resources/setup.md)). All are acceptable; the manual backend may use 5 instances
per level instead of 10, noted in the report.

Required:

- **A validator you wrote.** Never ask the model whether its own answer is
  correct. Your validator checks: is the path legal (contiguous, in-bounds, no
  walls)? Is the reported cost arithmetically right? Is it optimal against A*?
- **Three failure categories counted separately:**
  1. Illegal path
  2. Legal but suboptimal
  3. Legal and optimal but with an incorrect reported cost
- **A reproducibility measurement:** one instance, five identical calls, count
  distinct answers.
- **A scaling plot:** optimality rate vs. problem size, both systems, four sizes.

Then one additional arm:

- **Tool-augmented:** give the model your A* implementation as a callable tool
  (it emits a JSON call, you run the search, you return the result). Measure it as
  a third system. This arm is the preview of weeks 6–9 and it should perform
  differently from both others.

## Part 3 — Report (20 %)

`REPORT.md`, ≤ 2 000 words, containing:

1. **The Duel Scorecard**, fully filled in, three columns (classical, LLM,
   tool-augmented) — see [`resources/duel-scorecard.md`](../resources/duel-scorecard.md)
2. Your figures with captions that state what the reader should conclude
3. **"Where we may have been unfair"** — required, and genuinely graded. Address
   at minimum: did you tune your heuristic but use an untuned prompt? Is your
   instance distribution favorable to one side? Did you count your own
   development time?
4. A statement of what your evidence does **not** support. If your LLM solved 24/30
   at size 8, say explicitly what that tells you about size 20 (nothing).

## Grading

| Criterion | Weight |
|---|---|
| Correct implementations, passing tests | 25 % |
| Experimental protocol (sizes, instances, variance) | 25 % |
| Analysis quality — do the conclusions follow? | 25 % |
| Scorecard completeness and precision on axis 2 (guarantees) | 15 % |
| Honesty section | 10 % |

**We grade the experiment, not the verdict.** A careful study concluding "the LLM
did better than we expected" outscores a sloppy one concluding "classical wins."

## Common ways to lose points

- Single-instance measurements ("A* took 0.03 s")
- Reporting only means, with no variance
- One problem size, so no scaling claim is possible
- Using the LLM to validate the LLM
- Claiming BFS is "optimal" without the uniform-cost condition
- An honesty section that says "we were fair"
