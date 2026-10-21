# Week 0 — First Comparison: `sorted()` vs. an LLM

**Setup:** backend `ollama`, model `qwen2.5:3b`, temperature 0, seed 0, prompt fixed by the course
(fenced-code-block format). 20 instances (5 per size, sizes 5/10/20/40, seed 20250806).
Full raw outputs are in `.llm_cache/` (committed).

## Summary table (from the notebook, §6)

```
  system              n  solved    rate   median      p95
  -------------------------------------------------------
  sorted()           20      20   100%    0.00s    0.00s
  LLM                20       3    15%    0.01s  122.06s

  failure modes:
    LLM             invalid=9, malformed=3, wrong-but-confident=5

  solve rate by size  (axis 6 — look for the cliff)
                         5      10      20      40
  ------------------------------------------------
  sorted()           100%    100%    100%    100%
  LLM                 60%      0%      0%      0%
```

*Timing note:* the LLM median of 0.01s is misleading on its own — the table was produced on a
re-run where most calls were cache hits. The cache metadata shows real inference took ~2.8 s
(n=5) to ~4.8 s (n=40) per instance on CPU, and 3 of the n=40 calls hit the 120 s timeout
(recorded as `malformed`).

## Duel Scorecard

| Axis | sorted() | LLM |
|---|---|---|
| Correctness | 20/20 (100%) | 3/20 (15%) |
| Guarantee | Returns a permutation of the input in non-decreasing order, for **every** input, in O(n log n) — no conditions, no exceptions. | None. It produced a correct sort on 3 of these 20 instances at temp 0 with this prompt; no claim can be made about any other input, size, prompt, or temperature. |
| Cost | Effectively free: ~10⁻⁵ s of CPU, no model, no download. | ~2 GB model on disk, ~3–5 s of CPU per instance (up to 120 s timeout at n=40); $0 in API fees because it runs locally. |
| Latency | 0.00s / 0.00s | 0.01s / 122.06s (cached / p95; real inference ~3–5 s) |
| Reproducibility | Deterministic: same input always gives the same output. | At temperature 0: 3 runs, 1 distinct answer (reproducible). At temperature 1.0: 3 runs, 3 distinct answers (§5 measurement). |
| Scaling | 100% → 100% → 100% → 100% | 60% → 0% → 0% → 0% |
| Interpretability | Full certificate: the output can be checked (same multiset + non-decreasing) and the algorithm (Timsort) has a proof of correctness. | No certificate: the model outputs only the list, gives no trace of how it sorted, and its wrong answers look identical in form to its right ones. |
| Failure mode | none observed | invalid=9, malformed=3, wrong-but-confident=5 |

## The four questions from §6

**1. Did the LLM's solve rate fall as the list got longer?**
Yes, and abruptly: 60% at n=5 and 0% at every larger size. The cliff is between 5 and 10
elements for this model — earlier than expected, since the sorted *order* was often fine and
what broke was keeping the *contents* of the list intact.

**2. Which failure mode dominated?**
`invalid` (9 of 17 failures): the model dropped, duplicated, or invented numbers — e.g. on
`n10-3` it returned 10 perfectly ordered numbers but replaced 851 with a nonexistent 390.
That is a different problem from `wrong-but-confident` (5 failures: right numbers, a few out
of order), and it suggests a different fix — a multiset check, not a better sorting prompt.
The 3 `malformed` were 120 s timeouts at n=40.

**3. What did each solved instance cost?**
`sorted()`: microseconds, with an O(n log n) proof attached. The LLM: ~3 s of CPU per solved
instance (all at n=5), with no complexity claim of any kind — and at n=40 it sometimes spent
the full 120 s budget and returned nothing usable.

**4. Where might we have been unfair?** (honesty section)
- **Same information:** yes — both sides received exactly the same list of integers.
- **Tuning asymmetry:** it favors the classical side. `sorted()` is Timsort, decades of
  engineering; the LLM got one fixed, untuned prompt chosen by the course. A tuned prompt
  (e.g. asking it to verify its own count) might raise the LLM's rate — but tuning after
  seeing results would be p-hacking, so we report the frozen prompt.
- **Timeout policy:** the 120 s cap counts against the LLM as `malformed`; with a longer
  budget those 3 instances might have parsed (though based on the other n=40 outputs,
  probably not correctly).
- **A larger model** would likely move the cliff to larger n, but we cannot know where
  without running it — that is itself the point of measuring rather than assuming.

## Conclusion

An unreliable generator (15%) paired with a sound verifier is still usable — but only because
the verifier is sound. The most dangerous outputs were not the timeouts; they were the
`invalid` answers that *look* sorted and pass an eyeball check while silently losing data.
