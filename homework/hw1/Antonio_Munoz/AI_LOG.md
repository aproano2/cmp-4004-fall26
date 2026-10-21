# AI_LOG

Tool used throughout: Claude (claude.ai chat). The LLM used as the *subject* of the Part 2 duel (qwen2.5:3b via Ollama) is not logged here; it is in the report.

## HW1 — Understanding the assignment and the course repo
**Tool:** Claude
**What I asked:** To explain the assignment and the theory (admissibility, dominance, effective branching factor, proof by contradiction), and to read the course repo.
**What I got:** Step-by-step explanations and a map of what the repo already provides (search.py, gridworld.py, instance banks, reference solutions).
**What I did with it:** Followed the plan step by step. Asked my professor about using the reference solutions in `studios/*/solution.py`; he said it is allowed.
**Did I understand it?** Yes: BFS minimizes steps, not cost, so it is optimal only with uniform step costs; a heuristic is admissible if it never overestimates the true remaining cost.

## HW1 Part 1 — Classical implementations and tests
**Tool:** Claude
**What I asked:** Help getting BFS/DFS/UCS/IDS and the heuristics running in my folder.
**What I got:** Instructions to copy `studios/week-03/solution.py` and `studios/week-04/solution.py` (with the professor's permission) and a `run_tests.py` that runs the provided tests against my files.
**What I did with it:** Ran the provided tests (5 + 5 pass). Read `ids` and `depth_limited` to see how `hit_limit` decides whether to deepen.
**Did I understand it?** Yes: depth_limited returns hit_limit=True when the depth bound cut the search, so ids knows deeper levels may still find a solution; if it is False the space is exhausted.

## HW1 Part 1 — Instrumented engine, benchmark and analyses
**Tool:** Claude
**What I asked:** A harness that also measures max frontier, time and timeout; the four required analyses; a summary table and figures.
**What I got:** `engine.py`, `check_engine.py` (400 comparisons against the course code, 0 mismatches), `benchmark.py`, `analysis1-4.py`, `summary_part1.py`, `PROTOCOL.md`.
**What I did with it:** Ran everything and pasted the outputs back. A result that surprised me: h×3 expands MORE nodes than A* on the 8-puzzle at depth 16. Claude checked it was not a bug (re-expansions do not explain it); the cause is untested and is written as a hypothesis in the report.
**Did I understand it?** Yes: an expansion is a non-goal, non-stale node popped from the frontier whose successors are generated; IDS has no frontier, so I report recursion depth, which is not comparable.

## HW1 Part 2 — LLM client, validator, direct duel
**Tool:** Claude
**What I asked:** A cached Ollama client, my own validator, and a runner for the LLM on the grids.
**What I got:** `llm_client.py`, `duel_lib.py` (prompt, parser, validator), `test_validator.py`, `run_llm_duel.py`, `audit_llm.py`, `repro_llm.py`, `scaling_plot.py`.
**What I did with it:** Ran a pilot with free reasoning (2 of 3 replies cut by the 512-token cap) and switched to a direct-answer prompt with a 200-token cap. Added a sentence stating the cost convention so the model has the same information as A*. Handled HTTP 500 errors with retries. The audit showed 0/40 also with a lenient parser.
**Did I understand it?** Yes: illegal means invalid, out of bounds or not at the goal; suboptimal is legal but costlier than A*; wrong_cost is an optimal path with a wrongly summed cost. The validator recomputes everything, because asking the model would use the LLM to validate the LLM.

## HW1 Part 2 — Tool-augmented arm
**Tool:** Claude
**What I asked:** The arm where the model calls my A* as a tool.
**What I got:** `run_tool_arm.py` and the tool definition; patches to the client to send tools.
**What I did with it:** The first pilot failed because the model mis-copied the grid, so we changed the prompt to show the grid in the compact format the tool expects. Still 0 exact copies. I decided to run 5 instances per size instead of 10 because of time and declared it in the report.
**Did I understand it?** Yes: A* is optimal only for the grid it receives, so a mis-copied grid solves a different problem; that is why the single success does not show faithful formalization.

## HW1 Part 3 — Report
**Tool:** Claude
**What I asked:** A draft of `REPORT.md` from my results, and the numbers for the scorecard.
**What I got:** A draft with the scorecard, figure captions, the "Where we may have been unfair" section and the limits of the evidence, plus `scorecard_data.py`.
**What I did with it:** Pasted my real outputs; Claude's draft was checked against them and three claims were corrected (tool rejections 14 not 15, "several" loops instead of "often", who wrote which code).
**Did I understand it?** Yes: I checked the report numbers against my outputs and can explain each section, including what the evidence does not support.
