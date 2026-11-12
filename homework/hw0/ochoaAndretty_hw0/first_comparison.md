# First Comparison

## Prediction

I predict that the classical algorithm will win most of the comparisons because it is deterministic, while the LLM may make ordering or formatting errors.

## Experiment Summary

```text
system              n  solved   rate   median      p95
-------------------------------------------------------
sorted()           20      20   100%    0.00s    0.00s
LLM                20       3    15%   17.99s  122.33s

failure modes:
  LLM             invalid=9, malformed=3, wrong-but-confident=5

solve rate by size
                     5      10      20      40
------------------------------------------------
sorted()           100%    100%    100%    100%
LLM                 60%      0%      0%      0%
```

## Scorecard

| Axis             | sorted()                                                                                                         | LLM                                                                                                                                                          |
| ---------------- | ---------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Correctness      | 20/20 (100%)                                                                                                     | 3/20 (15%)                                                                                                                                                   |
| Guarantee        | If the input is a finite list of comparable integers, `sorted()` returns the same values in nondecreasing order. | If the response can be parsed and passes a verifier that checks its order and elements, the accepted answer is correct. The LLM alone provides no guarantee. |
| Cost             | `O(n log n)` time and `O(n)` auxiliary memory.                                                                   | One local model inference per problem, with considerably more computational and energy cost as the prompt and output grow.                                   |
| Latency          | 0.00s / 0.00s                                                                                                    | 17.99s / 122.33s                                                                                                                                             |
| Reproducibility  | 5 runs, 1 distinct answer.                                                                                       | 5 runs, 1 distinct parsed answer at temperature 0.0. However, the repeated answer was wrong in all five runs.                                                |
| Scaling          | 100% → 100% → 100% → 100%                                                                                        | 60% → 0% → 0% → 0%                                                                                                                                           |
| Interpretability | Yes. The result can be checked by confirming that it is ordered and contains exactly the original elements.      | Only if the response can be parsed. A verifier can check the proposed list, but malformed or invalid responses do not provide a usable certificate.          |
| Failure mode     | None observed                                                                                                    | invalid=9, malformed=3, wrong-but-confident=5                                                                                                                |

### Where we may have been unfair

* **Did both systems get the same information?**
  Both systems received the same lists and the same sorting goal. However, `sorted()` received the data directly as a Python list, while the LLM had to understand a text prompt and follow a strict output format.

* **Did you tune one side's parameters but use a default prompt for the other?**
  I did not tune the model or test several prompts before collecting the results. However, `sorted()` is already an optimized function designed specifically for this task, while the LLM is a small general-purpose model.

* **Is the instance distribution accidentally favourable to one side?**
  The instances probably favored `sorted()` because exact sorting is the task it was designed to solve. Longer lists also gave the LLM more opportunities to drop, change, or incorrectly order numbers.

* **Did you count the time spent writing the prompt or heuristic?**
  No. The reported latency only measured execution and did not include the time needed to write the prompt, parser, and verifier. Including this preparation would make the LLM approach more expensive.

* **Would a larger model change the result, and can you know without running it?**
  A larger model might perform better than `qwen2.5:3b`, but I cannot know without repeating the experiment. These results only describe the model and configuration that I tested.

## Answers to the Comparison Questions

1. **Did the LLM's solve rate fall as the list got longer?**
   Yes. The LLM solved 60% of the lists of size 5, but its success rate fell to 0% for sizes 10, 20, and 40. This shows a clear performance cliff as the lists became longer.

2. **Which failure mode dominated?**
   The dominant failure mode was `invalid`, with 9 cases. This means the LLM usually dropped, added, or changed numbers instead of preserving all the original elements.

3. **What did each solved instance cost?**
   The classical system had a median latency of approximately 0.00 seconds and solved all 20 instances. The LLM had a median latency of 17.99 seconds and a p95 latency of 122.33 seconds, while solving only 3 of 20 instances, so its correct results were much more computationally expensive.

4. **Where might the comparison have been unfair?**
   The comparison favored `sorted()` because it is specifically designed for sorting, while the LLM had to interpret a prompt, preserve every number, and follow an exact output format. The experiment also used only `qwen2.5:3b`, so the results cannot automatically be generalized to larger models.
