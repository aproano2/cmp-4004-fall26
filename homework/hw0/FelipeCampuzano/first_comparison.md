# Week 0 — First Comparison

## Summary

  system              n  solved    rate   median      p95
  -------------------------------------------------------
  sorted()           20      20   100%    0.00s    0.00s
  LLM                20       2    10%    0.00s  122.06s

  failure modes:
    LLM             invalid=10, malformed=3, wrong-but-confident=5

  solve rate by size  (axis 6 — look for the cliff)
                         5      10      20      40
  ------------------------------------------------
  sorted()           100%    100%    100%    100% 
  LLM                 40%      0%      0%      0% 


### 1. Did the LLM's solve rate fall as the list got longer?

Yes, the LLM solved 40% of instances with five elements, while the ones with lists of 10 elementrs and more had a solve rate of 0%. This indicates that the cliff scales the bigger the problem gets.

### 2. Which failure mode dominated?

The failure mode that was present most was 'invalid' with 10 instances. This indicates that the LLM either invented numbers or just discarded them, completely different from producing the correct numbers in the wrong order.

### 3. What did each solved instance cost?

The classical 'sorted()' implementation had effectively zero measured latency for these small instances. The LLM had much higher latency, with a reported p95 of 122.06 seconds, and only solved 2 of the 20 instances.

### 4. Where might we have been unfair?

The classic algorithm of sorting is deterministic, dessigned specifically to solve the problem of... sorting. The LLM was limited by a smaller model, so trying with a bigger model may have different results. Plus, the lime spent tuning the promt was not included in the latency. So a few disadvantages for the LLM.

## Scorecard

| Axis | sorted() | LLM |
|---|---|---|
| Correctness | 20/20 (100%) | 2/20 (10%) |
| Guarantee | 'sorted()' returns a sorted permutation for every valid input. | The LLM provides no correctness guarantee; its output must be verified. |
| Cost | Negligible computational cost for these small inputs. | Each uncached instance requires an LLM inference, which has substantially higher computational cost. |
| Latency | 0.00s / 0.00s | 0.00s / 122.06s |
| Reproducibility | Deterministic for the same input. | Reproducibility depends on the model, temperature, seed, and backend. It must be measured rather than assumed. |
| Scaling | 100% → 100% → 100% → 100% | 40% → 0% → 0% → 0% |
| Interpretability | The result can be directly checked as a sorted permutation of the input. | The generated list can be verified, but the model's reasoning does not provide a formal correctness certificate. |
| Failure mode | None observed. | invalid=10, malformed=3, wrong-but-confident=5 |

## Questions from Section 6

**### Where we may have been unfair**

**1. Did both systems get the same information?**

Yes, both systems received the same lists. The classical algorithm received the list directly, while the LLM received the same list inside the prompt. That means that neither system had extra information about the expected sorted result.

**2. Did you tune one side's parameters but use a default prompt for the other?**

Yes, this could be considered a disadvantage for the LLM. The classical 'sorted()' function is already specifically designed to sort lists, while the LLM depends on the prompt to understand the task and return the answer in the correct format. We also have to mention that we had to spend time tuning the parsers where as the sorting function does not need that type of additional process.

**3. Is your instance distribution accidentally favourable to one side?**

Well, possibly. The instances were generated randomly, equal conditions. But we do have to mention that it is easier for the single-purpose algorith, to handle the input better. The results show that the LLM struggled more with bigger lists.

**4. Did you count the time you spent writing the prompt? The heuristic?**

No. LAtency only includes the time needed to run the system, not tuning the prompt. This means the comparison is mainly measuring execution time, not takes into account all the tuning and additional time spent refining prompts.

**5. Would a larger model change the result — and can you know without running it?**

A larger model COULD potentially perform better, especially with the longer lists, but we cannot know for sure without testing it. To know whether model size makes a difference, we would need to run the same experiment with a larger model. But most likely, it will return better results.
