# AI use log — Duel 1 (Naranjo · Vega · Changotasig)

Per [`resources/ai-policy.md`](../../../resources/ai-policy.md). Append an entry
every time an AI assistant materially shapes work we submit. The last field is
the one that is graded.

---

## The engine and its equivalence tests

**Student:** Nicolás Naranjo
**Tool:** opencode
**What I asked:** implement the benchmark layer (engine + starter +
harness + tests) for BFS/DFS/UCS/IDS/A\* with max-frontier and a hard deadline,
and verify it against the course engines.
**What I got:** `engine.py` (one loop, four disciplines, goal test on
*expansion*, deadline checked per iteration), `starter.py` (thin graded layer so
the copied tests still import `starter`), `test_engine.py` asserting our
BFS/DFS/UCS ≡ `search.search` and our A\* ≡ `gridworld.astar` by *expansion
count* over all 80 instances, plus dominance, equal-cost and timeout tests.
**What I did with it:** ran it. First run hung for 15 minutes, it was because
IDS on a weighted grid is tree
search with no transposition table, so it expands ~3^depth; a 16×16 grid
burned 5 M expansions in 20 s without solving. I then changed the test to
assert `status == timeout` after a 2 s budget instead of waiting forever, and
kept that behaviour as a *documented* result rather than silently "fixing" it
with a closed set, adding one would have changed what IDS means. All 8 tests
pass in 17 s. the 120 s benchmark cell later confirmed 29 M expansions per
timeout.
**Did I understand it?** Yes, i made the search algorithms in past weeks and just needed
to copy them here and ways to test them and get their statistics.

---

## HW1 — benchmark, analyses, figures

**Student:** Nicolás Naranjo
**Tool:** opencode
**What I asked:** write `harness.py` (protocol: 4 levels × 10 instances × 7
algorithms, 120 s timeout, incremental CSV), `analyses.py` (the four required
analyses) and `plots.py`, then run them.
**What I got:** resumable raw CSVs with cost/length/expansions/max-frontier/
seconds and a `status` column. `summary.csv` with medians, Q1/Q3 and timeout
counts over solved runs only. The four analyses as their own CSVs plus a
rendered witness instance for the BFS failure. Six figures.
**What I did with it:** reviewed the statistics myself, medians with IQR, not
means. Timeouts reported as timeouts and excluded from medians but counted next
to them (a size where everything timed out must not show a zero).
**Did I understand it?** Yes, i made the search algorithms in past weeks and just needed
to copy them here and ways to test them and get their statistics.

---

## HW1 — independent review of Part 1 before submission

**Student:** Nicolás Naranjo
**Tool:** opencode (a read-only review sub-agent, then the main session)
**What I asked:** have a separate agent review the whole Part 1 submission
against `hw-1-search.md`, spec compliance, code correctness, statistics, docs.
Re-running the tests and recomputing the numbers itself instead of trusting our
pipeline, and reporting prioritized findings without touching any file.
**What I got:** no blockers, 18/18 tests and 260/260 median/IQR triples
independently reproduced, plus eight real defects: README claims that were off
by orders of magnitude (DFS "5–10× the optimal" is really 1.3×–22× on the grid.
"IDS at 16×16 always times out" is really 5 of 10), the grid arm of analysis 3
running `h × 8` while the spec says `× 3`, an off-by-one in the IDS
`max_frontier` counter, `ids_equals_ucs` reading a timeout as "not equal", a
figure title asserting a speedup the data does not show, a stale docstring, and
a broken relative link.
**What I did with it:** verified every claim against the raw CSVs before
acting, and one of its findings was wrong (it called two README links broken.
resolving them by hand showed only the `AI_LOG` link was), which is exactly why
I re-checked instead of applying the list blind. Then fixed all seven real
findings, re-ran the benchmark from scratch (656 s) and every analysis and
figure. Fixing the timeout/inequality confusion introduced a fresh bug of my own
`None != ""` made 5 timeouts count as solved — which the very next run
exposed as "40/40 solved" against a raw file that says 5 timed out.
**Did I understand it?** Yes. The sub-agent was only used to make sure no bugs slip
past me in part 1.

---

## HW1 — Part 2 (the duel)

**Student:** Andrés Vega
**Tool:** Claude Code (Claude Opus 5.5)
**What I asked:** implement Part 2 using the local model through our
`aicourse` client: a validator, the bare-LLM arm, the tool-augmented arm, the
reproducibility measurement, the scaling plot, and whatever else the spec
requires (report, cache committed).
**What I got:** `code/validator.py` (legality, true cost, optimality against
A\*, reported-cost check, with five categories counted separately),
`code/duel.py` (prompts, a tolerant JSON parser, the A\* tool loop, and the
reproducibility runs; latency is read back from the cache so that replays keep
the original timing), `code/test_validator.py` (19 tests, including A\* passing
its own validator on all 40 grids), `code/duel_plots.py` (figures 7–9), a local
`.gitignore` that re-includes `.llm_cache/`, and the Part 2 section
of the README. 167 real calls to `qwen2.5:3b`. A replay from the cache makes 0
calls and reproduces every LLM answer byte for byte.
**What I did with it:** Using the generated output, I manually reviewed the documents and results to examine the implementations and ensure everything made sense; if I didn't understand something, I asked the LLM to explain it.
**Did I understand it?** Yes

---

## HW1 — Part 2, second domain (8-puzzle duel)

**Student:** Andrés Vega
**Tool:** Claude Code (Claude Opus 5.5)
**What I asked:** add the 8-puzzle to the duel, with everything it needs
(results, figures, report).
**What I got:** puzzle checks in `code/validator.py` (blank stays on the
board, moves end on the goal, length optimal against A\*, reported cost) and
`code/duel_puzzle.py` (the same three systems; the tool takes the board state).
Also 11 more tests (30 in all), `fig10`–`fig12`, and the report and README
rewritten for both domains. The grid prompts were left byte-identical, so the
grid cache still replays (verified 40/40 hits).
**What I did with it:** I double-checked the model's output to review and understand it, and if I didn't understand a part, I asked the LLM to explain it to me.
**Did I understand it?** Yes

---

## HW1 — Part 2, puzzle results in one place

**Student:** Andrés Vega
**Tool:** Claude Code (Claude Opus 5.5)
**What I asked:** merge the puzzle's two runs into a single set of results.
**What I got:** `results/duel/puzzle/` now holds both runs in the same five
files, told apart by a `prompt` column (`v2` = main run, `v1` = archived first
run), with one section per version in `failures.md`. The `puzzle_v1/` folder
and the `--puzzle-v1` flag are gone, and the figures read only `v2`.
**What I did with it:** Just review that everithing is fine.
**Did I understand it?** Yes
