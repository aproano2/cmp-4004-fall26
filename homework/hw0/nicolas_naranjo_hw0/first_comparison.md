# Week 0 — First Comparison: `sorted()` vs. an LLM

## Summary

| system | n | solved | rate | median | p95 |
|---|---|---|---|---|---|
| sorted() | 20 | 20 | 100% | 0.00s | 0.00s |
| LLM | 20 | 3 | 15% | 0.00s | 120.00s |

failure modes:
- LLM: invalid=9, malformed=2, wrong-but-confident=6
- sorted(): none observed

Solve rate by size:
| | 5 | 10 | 20 | 40 |
|---|---|---|---|---|
| sorted() | 100% | 100% | 100% | 100% |
| LLM | 40% | 20% | 0% | 0% |

---

## Scorecard

| Axis | sorted() | LLM |
|---|---|---|
| Correctness | 20/20 (100%) | 3/20 (15%) |
| Guarantee | For every input containing a list of integers, sorted() returns a sorted list of integers. | Correct on 3/20. |
| Cost |  n log n comparisons. ~0.00s per instance. |  Median speed on successes, but 3 hit the 120s timeout, so cost is mostly because of failures. |
| Latency | 0.00s / 0.00s | 0.00s / 120.00s |
| Reproducibility |  Identical answer every run (deterministic). |  5 runs, 2 distinct answers, at temperature 0.0 (5 distinct at 1.0) |
| Scaling | 100% -> 100% -> 100% -> 100% | 40% -> 20% -> 0% -> 0% |
| Interpretability |  Output is an increasing permutation of the input. |  There is no guarantee the LLM is right, only verification works.|
| Failure mode | none observed | invalid=9, malformed=2, wrong-but-confident=6 |

---

## 1 · Did the LLM's solve rate fall as the list got longer?

Yes. The solve rate went 40% -> 20% -> 0% -> 0%, it completely fails at n=20+. Thats the cliff of the solve rate as input got longer.

## 2 · Which failure mode dominated?

The biggest failure was invalid responses, followed by wrong-but-confident.

## 3 · What did each solved instance cost?

The seconds it took to generate the answer (and some timeouts) in the case of the LLM, and for the sorted() it was n log n time.

## 4 · Where might you have been unfair?

Address at least three:

- [x] **Same information?** All runs had the same prompt and the same list.
- [x] **Tuned one side, defaulted the other?** There was no parameters tuned on either side, tests where run on the intial settings.
- [ ] **Instance distribution favourable to one side?** All random ints came from the same seed, which could still favor sorted() instead of the llm depending on the output.
- [ ] **Counted prompt / heuristic-writing time?** The one line sorted() call is simpler than the prompt used for the llm which takes more time, which could affect results.
- [ ] **Would a larger model change the result?** Most likely yes, but we cant be sure until we actually run the tests on a bigger model.
