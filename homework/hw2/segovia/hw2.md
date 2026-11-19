# Homework 2 — The Formalizer

**Assigned:** Week 9 · **Due:** Week 11 · **Weight:** 15 %
**Team size:** Studio groups. Include the names in the REPORT.md header.

---

## The task

In weeks 6–9 you met the same architecture three times, from three research groups
(Logic-LM, LINC, LLM-Modulo): **use the language model to translate natural
language into a formal specification, and use a sound solver to solve it.**

This homework tests that architecture properly. You pick one formalism, build all
three arms, and produce a real error taxonomy.

## Choose one target formalism

| Formalism | Solver | Good if you liked |
|---|---|---|
| **CSP** | your week 6 solver | week 6 |
| **SAT** | your week 7 DPLL | week 7 |
| **Prolog / FOL** | SWI-Prolog | week 8 |
| **PDDL** | pyperplan | week 9 |

## The three arms

| Arm | Pipeline | What it measures |
|---|---|---|
| **A — Hand** | you write the formal model (this doubles as your ground truth) → solver | the ceiling |
| **B — Hybrid** | LLM writes the model → solver | the architecture under test |
| **C — Direct** | LLM answers from the natural-language problem | the baseline to beat |

Plus **arm B′ — Hybrid with self-refinement**: when the solver reports an error
(parse failure, unsatisfiable, no plan), feed that error back to the model and
retry, max 3 iterations. Report B and B′ separately. **The delta between them is
the most interesting number in this duel** — it measures whether solver feedback is
a usable learning signal.

## Requirements

**Problem set.** You must construct your own dataset of at least 20 natural-language problems, complete with documented ground truth. These problems must span at least three difficulty levels (measured by a defensible metric: e.g., number of variables, constraints, or minimum plan length). You may adapt classic domains (such as Blocksworld, Einstein's riddle, or graph coloring) or invent your own, but you are responsible for writing the natural-language prompts and hand-verifying the correct answers to establish the ground truth.

**Instrumentation.** For every arm, per instance: correct / incorrect / no-answer,
wall-clock, tokens (if applicable), and solver time separately from LLM time.

**The error taxonomy** — the core deliverable. Classify **every** arm-B failure:

| Category | Detectable without ground truth? |
|---|---|
| Malformed syntax (won't parse) | **Yes** — solver rejects it |
| Valid syntax, over-constrained (no solution exists) | **Yes** — solver reports unsat |
| Valid syntax, under-constrained (multiple solutions, wrong one returned) | Sometimes |
| Valid model of the *wrong problem* (hallucinated or dropped premises) | **No** |
| Quantifier scope / arity errors | Sometimes |
| Solver timeout | Yes |

That "detectable without ground truth" column is the point of the whole homework. Fill
it in from your own data and discuss it: **an architecture whose failures announce
themselves is deployable in a way that one whose failures are silent is not.**

**The comparison that matters.** For arm C, how many of its wrong answers were
detectable without ground truth? (Usually: near zero.) Contrast directly with arm
B. State the engineering consequence.

## Deliverables

```
homework/hw2/{student_lastname}/
├── REPORT.md              ≤ 2 500 words
├── code/                  translation harness, refinement loop, arm runners
├── problems/              your 20 problems + ground truth
├── results/*.csv
├── fig/*.png              ≥ 3 figures, one of which is per-arm accuracy vs. difficulty
├── taxonomy.md            every arm-B failure, classified, with the model output
├── .llm_cache/
└── AI_LOG.md
```

## Report contents

1. **Duel Scorecard**, four columns (A, B, B′, C)
2. Accuracy vs. difficulty plot, all arms
3. The error taxonomy with counts and at least five verbatim examples of model
   output, each annotated with what went wrong
4. **The refinement analysis:** iterations-to-success distribution; what fraction
   never converged; whether failures that survive 3 rounds are qualitatively
   different from ones fixed in 1.
5. **Cost accounting:** cost per correct answer, not per attempt. An arm that is cheap and wrong is not cheap. (If using local models, calculate this using the equivalent per-token pricing of a hosted provider like Groq or Together AI, or estimate compute time).
6. **"Where we may have been unfair"**
7. **A recommendation.** Given a real deployment of this task, which arm would you
   ship and what monitoring would you attach? Defend it with your own numbers.

## Grading

| Criterion | Weight |
|---|---|
|Dataset construction & Experimental protocol (problem design, difficulty scaling, variance) | 15 %
| All four arms working correctly | 20 % |
| Error taxonomy — completeness and insight | 20 % |
| Refinement-loop analysis | 15 % |
| Experimental protocol (difficulty levels, instance count, variance) | 15 % |
| Cost-per-correct-answer accounting | 10 % |
| Honesty section + deployment recommendation | 5 % |

The taxonomy carries the most weight because it is the part that requires you to
look carefully at what actually happened rather than at a summary statistic.

## Notes

- Small local models produce malformed output frequently. That is a *finding*, not
  an obstacle — it populates your taxonomy. Report your model and its size
  prominently, since it conditions every result you have.
- If arm B beats arm A, suspect a bug in your hand-written model first. Check
  before you claim it. If it survives checking, say so — it is a legitimate and
  interesting result.
- Do not let the refinement loop see the ground-truth answer. Only the *solver's
  error message* may be fed back. Leaking the answer invalidates the arm, and it
  is an easy mistake to make.
