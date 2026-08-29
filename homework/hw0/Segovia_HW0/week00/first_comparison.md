# Week 0 — First Comparison

## Experimental setup

- **Classical system:** Python `sorted()`
- **LLM system:** Ollama with `qwen2.5:3b`
- **Task:** Sort integer lists in ascending order
- **Dataset:** 20 instances: five each at sizes 5, 10, 20, and 40
- **Verifier:** Checks that the output parses as a list, preserves the input multiset, and is in non-decreasing order
- **Cache:** `.llm_cache/` was enabled and retained as the experiment audit trail

## Summary

| System | Instances | Solved | Solve rate | Median latency | p95 latency |
|---|---:|---:|---:|---:|---:|
| `sorted()` | 20 | 20 | 100% | 0.00 s | 0.00 s |
| LLM | 20 | 3 | 15% | 0.00 s* | 122.05 s |

\*The recorded median was 0.00 s because previously computed answers were served from the cache. It should not be interpreted as the model's uncached inference time.

### Solve rate by problem size

| System | n = 5 | n = 10 | n = 20 | n = 40 |
|---|---:|---:|---:|---:|
| `sorted()` | 100% | 100% | 100% | 100% |
| LLM | 60% | 0% | 0% | 0% |

### Observed failure modes

| System | Invalid | Malformed | Wrong-but-confident |
|---|---:|---:|---:|
| `sorted()` | 0 | 0 | 0 |
| LLM | 9 | 3 | 5 |

The LLM failed on 17 of 20 instances. The dominant failure mode was `invalid`: in nine cases, the model dropped, invented, or changed elements instead of preserving the original multiset.

## Duel Scorecard

| Axis | `sorted()` | LLM |
|---|---|---|
| Correctness | 20/20 (100%) | 3/20 (15%) |
| Guarantee | For every valid list of comparable integers, `sorted()` returns a permutation of the input in non-decreasing order. | No general guarantee. A correct answer on an observed instance does not imply correctness on the next instance. |
| Cost | No paid service was used; local computation was negligible for these instances. | No paid API was used, but local CPU time, memory, and electricity were consumed. The slowest observed region reached a p95 latency of 122.05 s. |
| Latency | 0.00 s median / 0.00 s p95 at the displayed precision. | 0.00 s recorded median / 122.05 s p95. Cache hits explain the 0.00 s median, so it is not a fair estimate of uncached inference latency. |
| Reproducibility | Deterministic for the same input: one distinct sorted result is expected on every run. | On the paperclip probe, temperature 0.0 produced 2 distinct answers in 3 runs; temperature 1.0 produced 3 distinct answers in 3 runs. |
| Scaling | 100% → 100% → 100% → 100% | 60% → 0% → 0% → 0% |
| Interpretability | The output acts as a compact certificate: the verifier can check that it is ordered and preserves exactly the same multiset. The algorithm also has a known complexity bound. | The generated text is not a certificate of correctness. It must be parsed and independently verified because a plausible-looking list may omit, add, or misorder elements. |
| Failure mode | None observed | `invalid=9`, `malformed=3`, `wrong-but-confident=5` |

## Questions

### 1. Did the LLM's solve rate fall as the list got longer?

Yes. The LLM solved 60% of the five-element lists, but its solve rate fell to 0% at sizes 10, 20, and 40. This is a clear performance cliff. In contrast, `sorted()` maintained a 100% solve rate at every tested size.

### 2. Which failure mode dominated?

The dominant failure mode was `invalid`, with nine occurrences. This means the model changed the multiset by dropping, inventing, or replacing values. There were also three malformed outputs and five wrong-but-confident outputs.

### 3. What did each solved instance cost?

`sorted()` completed every instance with latency rounded to 0.00 seconds and no paid service. The LLM also used no paid API, but it required local computation and showed a p95 latency of 122.05 seconds. Because many LLM responses came from `.llm_cache/`, the recorded 0.00-second median does not represent uncached generation time; the comparison nevertheless shows that the classical method was both more reliable and computationally cheaper for this task.

### 4. Where might the comparison have been unfair?

First, the task strongly favors the classical system because sorting is exactly what `sorted()` is designed and proven to do, while a language model generates tokens rather than executing a certified sorting algorithm. Second, the experiment used a small local 3-billion-parameter model; a larger model might perform differently, but that cannot be claimed without testing it. Third, cached LLM responses distorted the latency summary, so the recorded median is not a clean comparison of uncached execution time. Finally, the prompt was carefully formatted for machine parsing, while the classical system did not need comparable prompt engineering.

## Failure Atlas entry for the class forum

### [Wk0] A correct arithmetic answer becomes unparseable prose

**Setup:** `qwen2.5:3b`, bare prompt `What is 17 * 23?`, parsed using the experiment's defensive integer parser.  
**Classical:** Python arithmetic returns 391 exactly.  
**LLM:** `17 * 23 equals 391.`  
**Category:** malformed  
**Why it matters:** Although a person can see the correct answer, an automated pipeline encounters several untagged numbers and cannot safely determine which one is the result, so downstream measurement can fail or silently record the wrong value.

## Suggested reply to a classmate

Your failure shows why checking only whether a list is ordered is not sufficient. I would also compare the input and output multisets, because that test detects a missing, duplicated, or invented number even when the output looks correctly sorted.
