"""Duel 1 / Part 2 — the duel: A* vs. a local LLM vs. an LLM with A* as a tool.

The single entry point. It runs both Part 1 domains through the same code:

    duel_grid.py     weighted grids, 5x5 / 8x8 / 12x12 / 16x16
    duel_puzzle.py   8-puzzle, optimal depths 4 / 8 / 12 / 16
    duel_core.py     everything shared: LLM calls, the tool loop, aggregation

Three systems per domain, every answer scored by ``validator.py`` (never by a
model):

    A*        A*+Manhattan from ``engine.py`` — the classical arm.
    LLM       qwen2.5:3b via ``aicourse`` (Ollama), given the instance as text
              and asked for the answer as JSON.
    LLM+tool  the same model and prompt, plus our A* as a callable tool: it
              emits a JSON call, we run the search and paste the result back,
              and the model writes its final answer (up to 3 calls).

All model calls run through the ``aicourse`` cache (``../.llm_cache/``,
committed): a rerun replays every transcript for free, and the cache is the
audit trail of every number. Temperature 0, seed 0; the reproducibility runs
add five calls at T = 0 and five at T = 0.7 per sampled instance.

Usage::

    python duel.py                    # both domains (replays from the cache)
    python duel.py --domain grid      # one domain: grid | puzzle

Outputs, one folder per domain::

    results/duel/grid/      raw.csv  summary.csv  repro.csv  repro_summary.csv  failures.md
    results/duel/puzzle/    (same, plus a ``prompt`` column: v2 = the main run,
                             v1 = the archived first run, see duel_puzzle.py)

Then ``python duel_plots.py`` draws the figures.
"""

from __future__ import annotations

import argparse

from duel_core import DEFAULT_MODEL, make_llm, run_domain
from duel_grid import GridDomain
from duel_puzzle import PuzzleDomain


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--domain", default="all", choices=["all", "grid", "puzzle"])
    ap.add_argument("--no-repro", action="store_true",
                    help="skip the reproducibility calls")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    args = ap.parse_args(argv)

    domains = []
    if args.domain in ("all", "grid"):
        domains.append(GridDomain())
    if args.domain in ("all", "puzzle"):
        domains.append([PuzzleDomain("v2"), PuzzleDomain("v1")])

    llm = make_llm(args.model)
    for dom in domains:
        run_domain(dom, llm, repro=not args.no_repro)
    print(f"[duel] real LLM calls this run: {llm.calls_made}")


if __name__ == "__main__":
    raise SystemExit(main())
