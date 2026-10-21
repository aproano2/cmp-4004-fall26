"""Provided tests for week-4 Task 1.

Run: ``python3 test_heuristics.py``. Passes ⇒ your Task 1 is defensible;
you are ready for Task 2. Prints one line per test.

The *failure* test — ``test_inadmissible_heuristic_returns_suboptimal_path``
— asserts that ``h_bad`` breaks optimality *at least once* across the bank.
That is the point of the exercise: watch a guarantee fail.
"""
import sys

from gridworld import GridProblem, astar, load_instances
import starter as s


def _optimal_cost(grid):
    """Ground truth: UCS (== A* with h=0) is optimal because all step costs > 0."""
    prob = GridProblem(grid)
    node, _ = astar(prob, lambda p, st: 0)
    assert node is not None
    return node.g


BANK = load_instances()


def test_h_zero_admissible_and_optimal():
    # h_zero is admissible by definition and A* should return the true optimum.
    for size in BANK:
        for grid in BANK[size]:
            prob = GridProblem(grid)
            node, _ = astar(prob, s.h_zero)
            assert node.g == _optimal_cost(grid), f"h_zero not optimal on {size}x{size}"
    print("  ok  h_zero admissible ⇒ optimal on all 40 grids")


def test_manhattan_scaled_is_admissible():
    # For every reachable state, h(state) must be <= true remaining cost.
    for size in BANK:
        for grid in BANK[size]:
            prob = GridProblem(grid)
            # remaining cost from every state = run A* from that state (h=0).
            # Sample: check start + goal + one interior point.
            for state in [prob.initial, prob.goal, (prob.rows // 2, prob.cols // 2)]:
                # remaining true cost from `state` to goal:
                sub = GridProblem(grid)
                sub.initial = state
                node, _ = astar(sub, lambda p, st: 0)
                h = s.h_manhattan_scaled(prob, state)
                assert h <= node.g + 1e-9, (
                    f"h_manhattan_scaled overestimates at {state} on {size}x{size}: "
                    f"h={h} > remaining={node.g}"
                )
    print("  ok  h_manhattan_scaled admissible on sampled states across 40 grids")


def test_manhattan_scaled_dominates_zero():
    # For a heuristic that dominates h_zero, A* should expand no more nodes.
    for size in BANK:
        for grid in BANK[size]:
            prob = GridProblem(grid)
            _, exp_zero = astar(prob, s.h_zero)
            _, exp_manh = astar(prob, s.h_manhattan_scaled)
            assert exp_manh <= exp_zero, (
                f"h_manhattan_scaled expanded MORE than h_zero on {size}x{size}: "
                f"{exp_manh} > {exp_zero}"
            )
    print("  ok  h_manhattan_scaled dominates h_zero (expansions never worse)")


def test_manhattan_scaled_returns_optimal_cost():
    for size in BANK:
        for grid in BANK[size]:
            prob = GridProblem(grid)
            node, _ = astar(prob, s.h_manhattan_scaled)
            assert node.g == _optimal_cost(grid), (
                f"h_manhattan_scaled not optimal on {size}x{size}"
            )
    print("  ok  h_manhattan_scaled preserves optimality on all 40 grids")


def test_inadmissible_heuristic_returns_suboptimal_path():
    """The point of the week. h_bad must break optimality at least once."""
    broken = 0
    total = 0
    for size in BANK:
        for grid in BANK[size]:
            prob = GridProblem(grid)
            node, _ = astar(prob, s.h_bad)
            true_opt = _optimal_cost(grid)
            if node.g > true_opt:
                broken += 1
            total += 1
    assert broken > 0, (
        f"h_bad returned optimal on ALL {total} instances — it is not actually "
        "inadmissible on this bank. Make it overestimate more aggressively."
    )
    print(f"  ok  h_bad broke optimality on {broken}/{total} instances "
          f"(and that is the lesson)")


TESTS = [
    test_h_zero_admissible_and_optimal,
    test_manhattan_scaled_is_admissible,
    test_manhattan_scaled_dominates_zero,
    test_manhattan_scaled_returns_optimal_cost,
    test_inadmissible_heuristic_returns_suboptimal_path,
]


def main():
    failed = 0
    for t in TESTS:
        try:
            t()
        except NotImplementedError:
            print(f"  --  {t.__name__}: heuristic not implemented yet")
            failed += 1
        except AssertionError as e:
            print(f"  FAIL {t.__name__}: {e}")
            failed += 1
    if failed:
        print(f"\n{failed}/{len(TESTS)} failed")
        sys.exit(1)
    print(f"\nall {len(TESTS)} tests pass")


if __name__ == "__main__":
    main()
