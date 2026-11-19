# Week 0 first comparison: `sorted()` vs. local LLM

## Setup

- Classical baseline: Python `sorted()`.
- LLM backend: `ollama`.
- LLM model: `qwen2.5:1.5b`.
- Prompt: sort the given list of integers and reply only with comma-separated integers inside a fenced code block.
- Problem sizes: 5, 10, 20, 40.
- Instances: 5 per size, 20 total.
- Cache: `.llm_cache/` kept as the audit trail for model responses.

## Summary table

| System | n | Solved | Solve rate | Median latency | p95 latency | Failure modes |
|---|---:|---:|---:|---:|---:|---|
| `sorted()` | 20 | 20 | 100% | 0.00s | 0.00s | none observed |
| LLM (`qwen2.5:1.5b`) | 20 | 4 | 20% | 7.23s | 122.09s | invalid=12, malformed=1, wrong-but-confident=3 |

The latency values above are from the first uncached model run. Later notebook runs may show lower median latency because cached completions return instantly; that is expected and is part of the audit trail.

## Scorecard

| Axis | `sorted()` | LLM (`qwen2.5:1.5b`) |
|---|---|---|
| Correctness | 20/20 (100%) | 4/20 (20%) |
| Guarantee | For every finite input list, Python `sorted()` returns the same multiset in non-decreasing order. | No formal guarantee; the result is only empirical for these 20 cached trials with this model, prompt, temperature, and seed. |
| Cost | Deterministic local computation, O(n log n), no model calls. | One local LLM call per instance; prompt and generation cost grow with list size and have no useful correctness bound. |
| Latency | 0.00s median / 0.00s p95. | 7.23s median / 122.09s p95 on the first uncached run. |
| Reproducibility | Deterministic: repeated runs return the same sorted list. | On the paperclip probe, temperature 0.0 produced 2 distinct answers in 3 runs; temperature 1.0 produced 3 distinct answers in 3 runs. Cache and fixed seeds make this experiment auditable, not guaranteed. |
| Scaling | 100% -> 100% -> 100% -> 100% for n=5,10,20,40. | 80% -> 0% -> 0% -> 0% for n=5,10,20,40. |
| Interpretability | The algorithm is inspectable, and correctness can be checked by order plus multiset equality. | The model returns text, not a certificate; correctness depends on external parsing and verification. |
| Failure mode | none observed | invalid=12, malformed=1, wrong-but-confident=3 |

## Four questions

1. The LLM solve rate fell as the list got longer. It solved 80% at n=5 and 0% at n=10, n=20, and n=40, while `sorted()` stayed at 100% for every size.
2. The dominant failure mode was `invalid`: 12 of the 16 LLM failures dropped, invented, or changed items. That is more serious than merely returning the right items in the wrong order, because a simple glance at sortedness may miss the data loss.
3. Each solved classical instance cost essentially 0.00s in this measurement and has an O(n log n) guarantee. Each LLM instance required a local model call, with 7.23s median latency and 122.09s p95 latency on the uncached run, and only 4 solved instances out of 20.
4. The experiment may be unfair in several ways: the prompt was fixed after a small prompt-format probe, not heavily tuned; a larger model might perform better; and the timing does not include the human time spent designing the prompt and verifier. Five instances per size also gives only a small estimate of variance.

## Failure Atlas entry

### [Wk0] LLM returns an unsorted list for five integers
**Setup:** `ollama`, `qwen2.5:1.5b`, temperature 0, prompt requested only a comma-separated sorted list inside a fenced code block.
**Classical:** `sorted([251, 38, 74, 434, 937])` returns `[38, 74, 251, 434, 937]`, verified by Python and by the multiset/order checker.
**LLM:** returned ````csv 251,38,74,434,937 ````. It preserved the input order instead of sorting.
**Category:** wrong-but-confident
**Why it matters:** The answer is parseable and contains the right numbers, so a pipeline that checks only the multiset would silently accept an unsorted result.
