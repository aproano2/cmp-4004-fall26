# The Duel Scorecard

This single rubric is used in **every week of the course**. By week 6 students
should reach for it without being asked; by week 14 they should be able to fill
one in for a system they have never seen.

The point of the scorecard is to replace *"the LLM felt smarter"* with a table
that survives a hostile reader.

---

## The eight axes

| # | Axis | Question it answers | How to measure it |
|---|------|--------------------|--------------------|
| 1 | **Correctness** | Does it produce a right answer? | % of instances solved correctly, on ≥ 30 instances |
| 2 | **Guarantee** | What does it promise *before* you run it? | Prose claim + the condition it depends on |
| 3 | **Cost** | What does one solved instance cost? | Tokens in/out, or node expansions, or wall-clock CPU |
| 4 | **Latency** | How long until an answer? | Median and p95 seconds per instance |
| 5 | **Reproducibility** | Same input twice → same output? | Run 5×, report how many distinct answers appear |
| 6 | **Scaling** | What happens as the problem grows? | A *curve*, not a point — see below |
| 7 | **Interpretability** | Can you explain *why* this answer? | Can you extract a checkable certificate? |
| 8 | **Failure mode** | When it breaks, *how* does it break? | Classify: wrong-but-confident, refuses, times out, malformed |

### Axis 2 is the one students undervalue

"Correct on my 30 test cases" and "provably optimal whenever *h* is admissible" are not the same kind of claim, and the difference is the entire subject of this course. Push students to state the guarantee as a conditional:

> A* returns a lowest-cost path **provided** *h* never overestimates the true
> remaining cost. No claim is made about runtime.

> The LLM returned a valid path on 27/30 instances. No claim is made about the
> 31st.

### Axis 6 is where the course lands

**One data point is not a result.** Every duel must report performance across a range of problem sizes. The characteristic finding is that LLM performance looks competitive on small instances and then falls off a cliff, while classical algorithms degrade along a predictable curve.

Minimum requirement: **at least four problem sizes, at least ten instances each.**

```
solve rate
  100% |●———●———●———●     ← A* (flat; cost grows, correctness doesn't)
       |     ○———○
   50% |          ╲○
       |            ╲
    0% |              ○   ← LLM (cliff)
       +——————————————————
        4    8   12   16    problem size
```

If a student's plot shows no cliff, that is an interesting result and they should say so and they must show the plot.

---

## Scoring

Each axis is scored on evidence quality, **not** on which system won:

| Score | Meaning |
|-------|---------|
| 0 | Not addressed |
| 1 | Asserted without evidence ("it was faster") |
| 2 | Measured once, on one instance |
| 3 | Measured across instances, with a summary statistic |
| 4 | Measured across instances *and* sizes, with variance reported and a stated limitation |

A student who runs a careful study concluding "the LLM won on this task" scores higher than one who runs a sloppy study concluding "classical won." **We grade the experiment, not the verdict.**

---

## Required table format

Every duel report includes this table, filled in:

| Axis | Classical | LLM | Hybrid | Evidence |
|------|-----------|-----|--------|----------|
| Correctness | 30/30 | 24/30 | 30/30 | `results/correctness.csv` |
| Guarantee | Optimal if *h* admissible | None | Optimal if solver verifies | — |
| Cost | 1 240 expansions (median) | 3 100 tokens | 3 100 tok + 1 240 exp | `results/cost.csv` |
| Latency | 0.03 s / 0.05 s | 4.1 s / 11.2 s | 4.3 s / 11.5 s | `results/latency.csv` |
| Reproducibility | 1 distinct answer | 4 distinct answers | 1 distinct | `results/repro.csv` |
| Scaling | see `fig/scaling.png` | cliff at n = 12 | flat | `fig/scaling.png` |
| Interpretability | path + cost proof | prose only | path + cost proof | — |
| Failure mode | times out at n > 20 | wrong-but-confident | malformed model → caught | `results/failures.md` |

---

## The honesty clause

Every report must include a section titled **"Where we may have been unfair."**

Ideas that belong there:

- Did you give both systems the same information?
- Did you tune the classical algorithm's parameters but use a default prompt (or the reverse)?
- Is your instance distribution accidentally favorable to one side?
- Did you count the time you spent writing the prompt? The time writing the
  heuristic?
- Would a larger model change the result, and can you know without running it?

This section is worth real credit. A student who identifies a genuine flaw in their own experiment has learned the thing this course is actually teaching.
