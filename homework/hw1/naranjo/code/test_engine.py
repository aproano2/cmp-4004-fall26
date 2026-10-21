"""Tests for our instrumented engine — it is not trusted on its own.

Run:  python3 code/test_engine.py      (from this folder: python3 test_engine.py)
  or:  pytest code/ -q

The engine is *our* code, so the first three tests check it against the course
engines we copied verbatim (``search.search`` and ``gridworld.astar``) over the
**whole** bank: same cost, same length, same expansion count. The rest pin the
properties Duel 1's analysis depends on: heuristic dominance, the A*-h1
equal-cost claim, the inadmissible heuristic actually breaking it, and the
timeout path returning "timeout" instead of "failure".
"""

import json
import random
import sys
from pathlib import Path

from gridworld import GridProblem, astar as course_astar, load_instances
from search import EightPuzzle, search as course_search

import starter as s
from engine import TIMEOUT, ids as engine_ids, search as engine_search


def _puzzle_bank():
    data = json.loads((Path(__file__).with_name("instances_puzzle.json")).read_text())
    return {int(k): [EightPuzzle(tuple(st)) for st in v]
            for k, v in data["instances"].items()}


PUZZLE_BANK = _puzzle_bank()
GRID_BANK = load_instances()          # gridworld default: instances.json (grids)
SIZES = {"puzzle": [4, 8, 12, 16], "grid": [5, 8, 12, 16]}


def _all_problems():
    for size in SIZES["puzzle"]:
        for prob in PUZZLE_BANK[size]:
            yield "puzzle", size, prob
    for size in SIZES["grid"]:
        for grid in GRID_BANK[size]:
            yield "grid", size, GridProblem(grid)


def test_bfs_dfs_ucs_match_course_engine():
    """fifo/lifo/priority must be byte-for-byte the same algorithm as
    ``search.search`` — cost, length and expansion count."""
    checked = 0
    for kind, discipline, course_kind in (("fifo", "fifo", "fifo"),
                                          ("lifo", "lifo", "lifo"),
                                          ("ucs", "ucs", "priority")):
        for domain, size, prob in _all_problems():
            mine = engine_search(prob, discipline)
            theirs_node, theirs_exp = course_search(prob, course_kind)
            assert mine.node is not None and theirs_node is not None
            assert mine.cost == theirs_node.g, (domain, size, kind, mine.cost, theirs_node.g)
            assert mine.length == len(theirs_node.path())
            assert mine.expansions == theirs_exp, (domain, size, kind,
                                                    mine.expansions, theirs_exp)
            checked += 1
    print(f"  ok  bfs/dfs/ucs identical to search.search on {checked} runs "
          f"(80 instances x 3 disciplines)")


def test_astar_matches_course_engine():
    """Our g+h discipline must be ``gridworld.astar`` — same best_g stale-entry
    rule, same tie-break counter, same expansion count."""
    checked = 0
    for domain, size, prob in _all_problems():
        for h in (s.h_zero, s.h_manhattan):
            mine = engine_search(prob, "astar", h=h)
            theirs_node, theirs_exp = course_astar(prob, h)
            assert mine.node is not None and theirs_node is not None
            assert mine.cost == theirs_node.g, (domain, size, h.__name__)
            assert mine.length == len(theirs_node.path())
            assert mine.expansions == theirs_exp, (domain, size, h.__name__,
                                                    mine.expansions, theirs_exp)
            checked += 1
    print(f"  ok  astar identical to gridworld.astar on {checked} runs")


def test_metrics_are_sane():
    """Every protocol column must be present and self-consistent.

    IDS is checked on the puzzles and the two small grid sizes only: on a grid
    it is tree search with a parent-skip and no closed set, so its work grows
    like 3^depth — at 16x16 it does not finish, which ``test_grid_ids_...
    below pins as an honest *timeout* rather than a hang.
    """
    checked = 0
    for domain, size, prob in _all_problems():
        for discipline in ("fifo", "lifo", "ucs"):
            r = engine_search(prob, discipline)
            assert r.status == "solved"
            assert r.max_frontier >= 1
            assert r.expansions >= 0
            assert r.generated >= r.expansions
            assert r.seconds >= 0.0
            assert r.length == len(r.node.path())
            checked += 1
        if domain == "grid" and size > 8:
            continue                      # IDS handled by the test below
        r = engine_ids(prob, timeout=30)
        assert r.status == "solved", (domain, size, r.status)
        assert r.max_frontier >= 1 and r.seconds >= 0.0
        checked += 1
    print(f"  ok  metrics present and consistent on {checked} runs")


def test_grid_ids_times_out_instead_of_hanging():
    """Known limitation, recorded on purpose: IDS on a 16x16 grid is an
    exponential tree search (no transposition table), so it hits the deadline.
    It must come back as status=timeout with partial metrics — never hang, and
    never be reported as "failed to solve"."""
    prob = GridProblem(GRID_BANK[16][0])
    r = engine_ids(prob, timeout=2.0)
    assert r.status == TIMEOUT, r.status
    assert r.node is None and r.expansions > 0 and 1.0 < r.seconds < 10.0
    print(f"  ok  grid IDS returns status=timeout after {r.seconds:.1f}s "
          f"({r.expansions:,} expansions) — reported as a timeout, not a failure")


def test_admissible_astar_equals_ucs():
    """Analysis 1's first claim: A* with an admissible h returns the same cost
    as UCS, on every instance of both domains."""
    for domain, size, prob in _all_problems():
        ucs = s.ucs(prob)
        for h in (s.h_manhattan, s.h_misplaced) if domain == "puzzle" else (s.h_manhattan,):
            a = s.astar(prob, h)
            assert a.cost == ucs.cost, (domain, size, h.__name__, a.cost, ucs.cost)
    print("  ok  A* (admissible) == UCS cost on all 80 instances")


def test_manhattan_dominates_misplaced_pointwise():
    """h_manhattan(s) >= h_misplaced(s) for every state we can reach — the
    premise of the dominance analysis. A violation is a bug in a heuristic."""
    random.seed(20260807)
    checked = 0
    for size, probs in PUZZLE_BANK.items():
        for prob in probs:
            state = prob.initial
            for _ in range(20):                 # seeded random walk
                state = prob.result(state, random.choice(prob.actions(state)))
                assert s.h_manhattan(prob, state) >= s.h_misplaced(prob, state), state
                checked += 1
            assert (s.h_manhattan(prob, prob.initial)
                    >= s.h_misplaced(prob, prob.initial))
            checked += 1
    print(f"  ok  h_manhattan >= h_misplaced on {checked} states (pointwise)")


def test_inadmissible_x3_breaks_optimality():
    """Analysis 3 needs the broken heuristic to actually break something."""
    broken = 0
    for size, probs in PUZZLE_BANK.items():
        for prob in probs:
            if s.astar(prob, s.h_manhattan_x3).cost > s.ucs(prob).cost:
                broken += 1
    assert broken > 0, "3x Manhattan never broke optimality — it is not inadmissible here"
    print(f"  ok  3x Manhattan broke optimality on {broken}/40 puzzle instances")


def test_timeout_is_a_timeout_not_a_failure():
    """A hard deadline must surface as status=timeout, with the metrics
    gathered up to that point — never as "no solution"."""
    prob = PUZZLE_BANK[16][0]
    r = engine_search(prob, "fifo", timeout=0.0)
    assert r.status == TIMEOUT, r.status
    assert r.node is None
    assert r.seconds < 1.0
    r2 = engine_ids(prob, timeout=0.0)
    assert r2.status == TIMEOUT, r2.status
    print("  ok  deadline returns status=timeout (not 'failed to solve')")


TESTS = [
    test_bfs_dfs_ucs_match_course_engine,
    test_astar_matches_course_engine,
    test_metrics_are_sane,
    test_grid_ids_times_out_instead_of_hanging,
    test_admissible_astar_equals_ucs,
    test_manhattan_dominates_misplaced_pointwise,
    test_inadmissible_x3_breaks_optimality,
    test_timeout_is_a_timeout_not_a_failure,
]


def main():
    failed = 0
    for t in TESTS:
        try:
            t()
        except AssertionError as e:
            print(f"  FAIL {t.__name__}: {e}")
            failed += 1
    if failed:
        print(f"\n{failed}/{len(TESTS)} failed")
        sys.exit(1)
    print(f"\nall {len(TESTS)} tests pass")


if __name__ == "__main__":
    main()
