# Duel 1 — Search

**Team:** Naranjo · Vega · Changotasig · **Parts:** 1 (classical comparison) and 2 (the duel); the write-up is [`REPORT.md`](REPORT.md).
Spec: [`../../hw1/hw-1-search.md`](../../hw1/hw-1-search.md).

Two domains, five algorithms, four difficulty levels, ten instances per level,
one hard timeout, medians and IQRs.

---

## The assignment, in short (Part 1 of [`hw-1-search.md`](../../hw1/hw-1-search.md))

**Domains:** 8-puzzle (every move costs 1) and weighted grid pathfinding
(terrain `.` = 1, `,` = 3, `~` = 8).
**Algorithms:** BFS, DFS, UCS, IDS, A\* (with several heuristics).
**Measurements, per algorithm per domain:** solution cost, solution length,
node expansions, maximum frontier size, wall-clock time.
**Protocol:** four difficulty levels (puzzle solution depths 4/8/12/16; grids
5×5/8×8/12×12/16×16), ten instances each, a **stated hard timeout** (we use
120 s), medians **and IQRs** — never a single run, never a bare mean. Timeouts
are reported as timeouts, not as failures to solve.
**Four required analyses:**

1. UCS and A\* with an admissible h return equal-cost solutions; BFS does **not**
   when step costs differ — show the instance where BFS is suboptimal.
2. Heuristic dominance: Manhattan expands no more nodes than misplaced-tiles on
   *every* instance (a counterexample is a bug in a heuristic, not a result).
3. Break admissibility (`h × 3`): report the speedup **and** the cost in
   solution quality. Both, or the analysis is incomplete.
4. Effective branching factor b\* for A\* with each heuristic.

**Where every number comes from**

| Question | File |
|---|---|
| raw per-run measurements (all 5 metrics + `status`) | `results/raw_puzzle.csv`, `results/raw_grid.csv` |
| medians, Q1/Q3, solved/timeout counts | `results/summary.csv` |
| analysis 1 — equal cost, and the BFS failure witness | `results/analysis1_optimality.csv`, `results/analysis1_bfs_worst_instance.txt` |
| analysis 2 — dominance, per instance + pointwise | `results/analysis2_dominance.csv` |
| analysis 3 — speedup and cost of `h × 3` (both domains; grid also carries the studio's ×8) | `results/analysis3_inadmissible.csv` |
| analysis 4 — b\* per heuristic per size | `results/bstar.csv` |
| figures | `fig/fig1` … `fig6` (six PNGs, ≥ 3 required) |

---

## Running it

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Then, from `code/`:

```bash
python3 test_search.py        # provided week-3 tests   (5/5)
python3 test_heuristics.py    # provided week-4 tests   (5/5)
python3 test_engine.py        # our engine vs the studio engines (8/8)
python3 harness.py            # benchmark  -> ../results/raw_*.csv + summary.csv   (~11 min)
python3 analyses.py           # the four required analyses -> ../results/*.csv
python3 plots.py              # six figures -> ../fig/*.png
```

`harness.py` is resumable: rows are appended and flushed as they arrive, so
re-running skips what already exists (`--fresh` starts over, `--timeout N`
changes the deadline).

**Expected runtime:** the 8-puzzle domain takes ~5 s. The grid domain takes
~11 min, dominated by IDS: 5 of its 10 runs at 16×16 burn the full 120 s each
(see below).

---

## File map

| File | Where it came from | Edit? |
|---|---|---|
| `code/search.py` | copied verbatim from `studios/week-03` | ❌ |
| `code/instances_puzzle.json` | copied from `studios/week-03/instances.json` | ❌ |
| `code/gridworld.py` | copied verbatim from `studios/week-04` | ❌ |
| `code/instances.json` | copied verbatim from `studios/week-04` — **this is the GRID bank** | ❌ |
| `code/test_search.py`, `code/test_heuristics.py` | copied verbatim, run unmodified | ❌ |
| `code/engine.py` | **ours** — instrumented search (frontier size + deadline) | ✅ |
| `code/starter.py` | **ours** — the five algorithms + both domains' heuristics | ✅ |
| `code/harness.py` | **ours** — the benchmark protocol | ✅ |
| `code/analyses.py` | **ours** — the four required analyses | ✅ |
| `code/plots.py` | **ours** — figures | ✅ |
| `code/test_engine.py` | **ours** — engine vs. the studio engines, 8 tests | ✅ |

⚠️ **Naming gotcha:** `gridworld.load_instances()` defaults to `instances.json`
next to it, which here is the *grid* bank. The puzzle bank is
`instances_puzzle.json` and is always passed explicitly. Never call
`search.load_instances()` with no argument in this folder.

Both instance banks are the seeded studio banks (seed `20260807`, 40 + 40
instances, 10 per level) — the levels already match the spec exactly
(8-puzzle depths 4/8/12/16; grids 5×5/8×8/12×12/16×16), so nothing is generated.

---

## Things you need to know before reading the results

1. **IDS on grids times out on purpose.** The studio IDS is tree search with a
   parent-skip and no transposition table, so its work grows like ~3^depth on a
   grid full of loops: at 16×16 it expands ~29 million nodes in 120 s without
   finishing — 5 of the 10 instances time out (the other 5 are shallow enough
   to solve: 0.9–34 s). Those rows say `timeout`, never `failed`. It is also
   the most interesting row in the grid table — IDS buys memory, not time.
2. **DFS is complete here but never optimal.** On the weighted grid it returns
   paths 1.3×–22× the optimal cost; on the puzzle, paths up to 94,280 moves
   long against an optimum of 4–16 (its single worst run). That is not a bug,
   it is the guarantee it never made.
3. **BFS is optimal on the puzzle and not on the grid.** Uniform costs on one
   domain, terrain 1/3/8 on the other. `results/analysis1_bfs_worst_instance.txt`
   shows the witness instance.
4. **Medians over solved runs only**, with `n_timeout` next to them in
   `results/summary.csv`.
5. **`max_frontier` for IDS is call-stack depth** (limit + 1 frames, i.e. the
   O(b·d) memory argument), not a frontier/heap size like BFS/DFS/UCS/A\*.
   It sits in the same column only because it is the memory metric IDS has.
6. **The 16×16 IDS median is over 5 solved instances only**, and those are the
   shallower ones — so it is systematically easier than BFS/UCS/A\*'s
   10-instance medians at that size. Read it next to `n_timeout = 5`.
7. **`generated` is not one of the five required metrics** and counts pushes
   differently (A\* only counts pushes that improve `g`), so do not compare it
   across algorithms. Everything the report needs is cost, length, expansions,
   `max_frontier`, seconds.

---

## Part 2 — the duel (A\* vs. a local LLM vs. LLM + A\* tool)

**Domains:** both Part 1 banks, as text. The 40 weighted grids
(5×5/8×8/12×12/16×16) and the 40 8-puzzles (depths 4/8/12/16), ten per level.
**Model:** `qwen2.5:3b` (Q4_K_M) through Ollama, via the course client in
`aicourse/` (temperature 0, seed 0, cached in `.llm_cache/`).

```text
code/
  duel.py            the single entry point: runs both domains
  duel_core.py       shared machinery: cached LLM calls, the three systems,
                     the A* tool loop, reproducibility, aggregation, output files
  duel_grid.py       grid domain only: prompts, parser, A* tool, validator hook
  duel_puzzle.py     8-puzzle domain only: the same five pieces
  validator.py       the checker for both domains; never asks a model
  test_duel.py       30 tests
  duel_plots.py      fig7-fig9 (grid), fig10-fig12 (puzzle)
results/duel/
  grid/  puzzle/      same five files in each; puzzle files add a `prompt` column
    raw.csv            one row per (system, instance): category, optimal/true/reported
                       cost, seconds, tokens, tool calls, expansions, validator reasons
    summary.csv        per system per size: counts per category, optimality rate,
                       latency median/IQR/p95, tokens
    repro.csv          5 calls per (instance, temperature) and each answer
    repro_summary.csv  distinct answers per cell
    failures.md        every non-optimal answer: instance, validator reasons,
                       model output verbatim
```

The validator checks the grid for legality (contiguous, in bounds, no walls,
S→G) and the puzzle for legality (every blank move on the board, ending on the
goal). In both domains it then checks the true cost, optimality against A\*,
and the reported cost. A\*'s own answers pass through it too (80/80 optimal).

The puzzle files hold two runs, told apart by the `prompt` column (and by one
section each in `failures.md`). `v2` is the main run, and every number in the
report and every figure use it. `v1` is the **first** run: its format example
(`["U", "L", ...]`) was copied by the model, so it is kept as evidence
(REPORT §5). `duel.py` replays both from the cache.

```bash
ollama pull qwen2.5:3b && ollama serve      # once
cd code
python test_duel.py        # 30/30
python duel.py             # both domains: ~1 h cold; seconds from .llm_cache/
python duel.py --domain grid          # or one domain
python duel_plots.py
```

`duel.py` replays from the cache: with `.llm_cache/` present it makes zero model
calls and regenerates every LLM answer identically. Only A\*'s wall-clock is
re-measured. Latency is read back from the cache record, so a replay still
reports the original inference time.

---

## Deliverable checklist (spec §Deliverables)

- [x] `code/` — implementations + benchmark harness (+ the duel: `duel*.py`, `validator.py`)
- [x] `results/*.csv` — raw measurements (+ summary + analysis tables; duel tables in `results/duel/`)
- [x] `fig/*.png` — twelve figures (≥ 3 required)
- [x] `REPORT.md` — ≤ 2 000 words
- [x] `AI_LOG.md` — per `resources/ai-policy.md`
- [x] `.llm_cache/` — every model transcript, committed (re-included by the
      local `.gitignore`, since the root one ignores all dotfiles)
