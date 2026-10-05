# Week 0 — First Comparison: sorted() vs LLM (qwen2.5:1.5b)

## Summary table

| system   | n  | solved | rate | median  | p95      |
|----------|----|--------|------|---------|----------|
| sorted() | 20 | 20     | 100% | 0.00s   | 0.00s    |
| LLM      | 20 | 5      | 25%  | 0.00s   | 122.05s  |

**Failure modes (LLM):** invalid=11, malformed=1, wrong-but-confident=3

**Solve rate by size (axis 6):**

|          | n=5  | n=10 | n=20 | n=40 |
|----------|------|------|------|------|
| sorted() | 100% | 100% | 100% | 100% |
| LLM      | 80%  | 20%  | 0%   | 0%   |

## Scorecard

| Axis | sorted() | LLM |
|---|---|---|
| Correctness | 20/20 (100%) | 5/20 (25%) |
| Guarantee | Always returns a correct permutation of the input in sorted order, for any input — a mathematical guarantee, not a statistic. | No guarantee. It produced a correct sort on 5 of 20 instances; nothing can be claimed about the 21st instance without testing it. |
| Cost | O(n log n) comparisons, proven, negligible CPU time. | ~1 forward pass per instance on qwen2.5:1.5b (CPU); expensive and highly variable with list length. |
| Latency | 0.00s / 0.00s | 0.00s / 122.05s |
| Reproducibility | Deterministic — same input always gives the same output. | Not tested at temperature 0 in this run, but section 5 showed 2-3 distinct answers out of 3 runs on an unrelated prompt, so the LLM is likely not fully reproducible even at temp 0. |
| Scaling | 100% → 100% → 100% → 100% | 80% → 20% → 0% → 0% |
| Interpretability | Yes — the algorithm's steps and correctness proof can be inspected directly. | No — cannot extract a certificate of correctness from the model's output; it must be checked externally by the verifier. |
| Failure mode | none observed | invalid=11, malformed=1, wrong-but-confident=3 |

### Where we may have been unfair

- **Same information:** Both systems received the exact same list of integers as input, so this axis is fair.
- **Prompt tuning:** The LLM prompt was written once, before collecting data (as instructed), and not iterated on after seeing results, so no p-hacking occurred. However, no comparable "tuning effort" was spent on the classical side because `sorted()` needs none — this is inherently asymmetric but reflects the real-world cost difference.
- **Model size:** qwen2.5:1.5b is a small model chosen because of local RAM constraints (8GB). A larger model (e.g. qwen2.5:3b or a frontier API model) would very likely solve more instances, especially at n=40. This result is specific to this model, not to "LLMs" in general.
- **Time cost not counted:** The time to write and test the prompt itself was not included in the latency numbers, only inference time was measured.

## Answers to the four questions (§6)

**1. Did the LLM's solve rate fall as the list got longer?**
Yes, clearly. It dropped from 80% at n=5, to 20% at n=10, to 0% at both n=20 and n=40. This is the "cliff" the course describes: the model handles very short lists reasonably but collapses almost completely once the list is longer than about 10 items.

**2. Which failure mode dominated?**
`invalid` dominated (11 of 20), meaning the model most often dropped, invented, or duplicated numbers rather than just returning them in the wrong order. Only 3 cases were `wrong-but-confident` (right numbers, wrong order) and 1 was `malformed` (unparseable). This suggests the main problem is the model losing track of the full list, not a reasoning/ordering failure.

**3. What did each solved instance cost?**
`sorted()` solved all 20 instances in effectively 0.00s (median and p95). The LLM's p95 latency was 122.05s per instance, and even the solved instances took non-trivial time on CPU. `sorted()` is also O(n log n) with a formal proof; the LLM has no such guarantee and its cost grows with response length and model uncertainty, not just list size in a predictable way.

**4. Where might we have been unfair?**
See "Where we may have been unfair" above — the main concerns are model size (a small 1.5B model on CPU is a weak baseline for the LLM side) and the lack of any prompt iteration budget spent on the LLM side despite the classical side needing zero tuning.