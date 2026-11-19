Model: `qwen2.5:3b` · temperature 0.7 · runs 3 · N per arm = 60 (problem×run)

| metric | A — Hand | B — Hybrid | B′ — Refinement | C — Direct |
|---|---|---|---|---|
| N (problem×run) | 60 | 60 | 60 | 60 |
| correct | 60 | 0 | 0 | 22 |
| incorrect | 0 | 4 | 4 | 33 |
| no-answer | 0 | 56 | 56 | 5 |
| accuracy | 1.000 | 0.000 | 0.000 | 0.367 |
| ci95_lo | 0.940 | 0.000 | 0.000 | 0.256 |
| ci95_hi | 1.000 | 0.060 | 0.060 | 0.493 |
| std_across_runs | 0.000 | 0.000 | 0.000 | 0.024 |
| accuracy_when_answered | 1.000 | 0.000 | 0.000 | 0.400 |
| wrong_announced | 0 | 56 | 56 | 5 |
| wrong_silent | 0 | 4 | 4 | 33 |
| silent_wrong_rate | 0.000 | 0.067 | 0.067 | 0.550 |
| mean_wall_s | 0.000 | 31.899 | 142.593 | 2.742 |
| mean_llm_s | 0.000 | 31.897 | 142.589 | 2.741 |
| mean_solver_s | 0.000 | 0.000 | 0.000 | 0.000 |
| mean_prompt_tokens | 0.000 | 471.800 | 3575.950 | 234.400 |
| mean_completion_tokens | 0.000 | 826.250 | 3384.983 | 56.600 |
| mean_attempts | 1.000 | 1.000 | 2.867 | 1.000 |

B vs B′ (paired): B′ fixes 0 instances, B-only wins 0; exact McNemar p = 1.0000. (B′ attempt 1 is B's call, so B-only wins should be 0.)

Detectability of wrong answers

| arm | wrong | announced | silent | frac announced |
|---|---|---|---|---|
| A — Hand | 0 | 0 | 0 | n/a |
| B — Hybrid | 60 | 56 | 4 | 0.933 |
| B′ — Refinement | 60 | 56 | 4 | 0.933 |
| C — Direct | 38 | 5 | 33 | 0.132 |

Cost

| arm | completion_tokens | correct | prompt_tokens | tokens_per_attempt | tokens_per_correct | wall_s_per_correct |
|---|---|---|---|---|---|---|
| A — Hand | 0 | 60 | 0 | 0 | 0 | 0.00042107 |
| B — Hybrid | 49575 | 0 | 28308 | 1298.05 | inf | inf |
| B′ — Refinement | 203099 | 0 | 214557 | 6960.93 | inf | inf |
| C — Direct | 3396 | 22 | 14064 | 291 | 793.636 | 7.47871 |