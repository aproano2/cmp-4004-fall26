# Capstone Project

**Proposal due:** Week 12 
---

## The task

Choose a problem. Solve it three ways — classical, LLM, hybrid. Benchmark all
three honestly. Recommend one for deployment and defend the recommendation with
your own evidence.


## Requirements

### The problem

Must have all four properties:

1. **A checkable notion of correctness** — you can decide whether an answer is
   right without asking a language model
2. **A tunable difficulty parameter** — you can generate easy and hard instances
3. **At least 100 instances** available or generable
4. **Small enough to run on a laptop** — no GPU, no paid API required

### The three arms

| Arm | Requirement |
|---|---|
| **Classical** | Implemented by you, using a technique from weeks 3–13. State its guarantee. |
| **LLM** | Any backend from [`resources/setup.md`](../resources/setup.md). Prompt engineering is legitimate work; document what you tried. |
| **Hybrid** | A real division of labor, not a coin flip. Justify where you drew the line. |

Hybrid architectures that count:

- LLM translates NL → formal model, your solver solves it (weeks 6–9)
- LLM proposes, your sound verifier checks and rejects (week 9)
- LLM generates candidate heuristics, your evaluator scores them (week 11)
- Classical algorithm runs, LLM explains the result in natural language
- LLM handles the messy input parsing, classical handles the combinatorics

### The benchmark

- **≥ 100 instances**, across **≥ 4 difficulty levels**
- **≥ 3 seeds** for anything stochastic
- Error bars on every aggregate number
- **An ablation:** remove one component of your hybrid and show what it was worth.
  A hybrid whose ablation shows no effect had a decorative component — that is a
  valid and publishable finding, and you should report it.
- **A failure taxonomy** for each arm, following Duel 2's format

## Deliverables

```
project/{lastname}
├── REPORT.md              ≤ 4 000 words
├── README.md              how to reproduce every number, from a clean clone
├── code/
├── data/                  instances + ground truth
├── results/*.csv          raw, all runs
├── fig/*.png              ≥ 5 figures
├── slides.md              8-minute presentation
├── .llm_cache/
└── AI_LOG.md
```

`README.md` must let a reader reproduce your headline result. This is graded: a
result nobody else can regenerate is not a result.

## Report structure

1. **Problem and motivation** — why is this worth three implementations?
2. **Classical approach** — technique, guarantee, and the condition it depends on
3. **LLM approach** — prompts, backend, model size, what you tried and discarded
4. **Hybrid architecture** — a diagram, and a defense of where you split the work
5. **Experimental design** — instances, difficulty parameter, metrics, seeds
6. **Results** — the Duel Scorecard, plus the scaling plot, plus the ablation
7. **Failure analysis** — taxonomy per arm, and which failures are silently
   undetectable
8. **Where we may have been unfair**
9. **Deployment recommendation** — which arm ships, under what monitoring, and what
   would change your mind
10. **What we would do with three more months**

## Grading

| Criterion | Weight |
|---|---|
| All three arms working | 15 % |
| Experimental design (instances, levels, seeds, error bars) | 20 % |
| The ablation | 10 % |
| Failure analysis | 15 % |
| Reproducibility (can we rerun it?) | 10 % |
| Report clarity and honesty section | 15 % |
| Presentation | 15 % |

## Proposal (due week 12, ungraded but required)

One page:

- The problem, and how you check correctness
- Your difficulty parameter
- Instance source: generated or found? How many?
- Planned classical technique and its guarantee
- Planned hybrid split
- The riskiest part of your plan

I will return comments within a week. Proposals that fail the four
problem-properties test get redirected early, which is the point of having them.

## Suggested problems

Each has a checkable answer, a difficulty knob, and generable instances.

| Problem | Classical | Difficulty knob | Hybrid idea |
|---|---|---|---|
| Course timetabling | CSP + AC-3 | # courses/constraints | LLM parses NL requirements → CSP |
| Sudoku variants (Killer, Jigsaw) | CSP | grid size, clue count | LLM reads the rules → constraints |
| Logistics planning | PDDL + pyperplan | # packages, cities | LLM writes the problem file |
| Word ladders / puzzle solving | BFS/A* | word length, distance | LLM proposes intermediates, BFS verifies |
| Nurse rostering | CSP or GA | # nurses, shift rules | LLM parses policy text → constraints |
| Circuit SAT / verification | DPLL | # variables, clauses | LLM writes the spec |
| Route planning with constraints | A* | map size, constraint count | LLM interprets "scenic but fast" |
| Recipe/menu planning under nutrition constraints | CSP or ILP | # meals, constraints | LLM handles NL dietary requests |
| Game-playing (Othello, Nim variants) | minimax + α-β | search depth, board size | LLM for opening book, α-β for tactics |
| POS tagging or NER on a low-resource language | HMM + Viterbi | corpus size | LLM few-shot vs. HMM |
| Spam/topic classification | Naive Bayes | # classes, class balance | LLM for hard cases only, NB for the rest |
| Grid-world agent under uncertainty | MDP / value iteration | grid size, noise | LLM as policy, classical as verifier |

Original problems are encouraged and often produce better projects. Propose early.

## Notes on scope

The most common failure is choosing an ambitious problem and running out of time
for the *evaluation*, which is where 45 % of the marks are. A modest problem with a
rigorous benchmark scores far higher than an ambitious one with three anecdotes.

Pick something you can finish, then spend your remaining time measuring it
properly.
