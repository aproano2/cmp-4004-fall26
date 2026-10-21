"""Provided tests for the week-3 studio.

Run: ``python3 test_search.py``. Prints one line per test. Passing means your
four algorithms behave the way the theory says they must -- INCLUDING the one
that must behave *badly*:

``test_bfs_suboptimal_nonuniform_cost`` asserts BFS returns a NON-optimal path.
Every year someone reports it as a bug. It is not. BFS is optimal only when step
costs are uniform; ``TinyGraph`` breaks that condition on purpose. Watching a
guarantee fail once is how you learn the guarantee is real.
"""
import sys

from search import EightPuzzle, TinyGraph, Problem, D8
import starter as s


# depth-8 instance: optimal solution length is 8, verified by exhaustive BFS
# from the goal (see _generate_instances.py). BFS/UCS/IDS must all return 8.
D8_OPTIMAL_LEN = 8


class CyclicGraph(Problem):
    """A graph with a 3-cycle A->B->C->A plus an exit C->G. A DFS with NO explored
    set would loop on the cycle forever; the given search() has one, so DFS must
    terminate and reach G."""
    EDGES = {"A": ["B"], "B": ["C"], "C": ["A", "G"], "G": []}

    def actions(self, state):
        return self.EDGES[state]

    def result(self, state, action):
        return action


def test_bfs_optimal_uniform_cost():
    # 8-puzzle: every move costs 1, so BFS IS optimal here.
    node, _ = s.bfs(EightPuzzle(D8))
    assert node is not None, "bfs found no solution"
    assert len(node.path()) == D8_OPTIMAL_LEN, (
        f"bfs length {len(node.path())} != optimal {D8_OPTIMAL_LEN}"
    )
    print(f"  ok  bfs optimal on uniform costs (len={D8_OPTIMAL_LEN})")


def test_bfs_suboptimal_nonuniform_cost():
    """THE point of the exercise. BFS counts edges, not cost. On TinyGraph the
    fewest-edges path to the goal costs 10; the optimal path costs 2. BFS must
    return the WRONG (cost-10) answer -- its optimality guarantee does not hold
    when step costs differ."""
    node, _ = s.bfs(TinyGraph("start", "A"))
    assert node is not None
    assert node.g == 10, (
        f"expected BFS to return the suboptimal cost-10 path, got g={node.g}. "
        "If you got 2, check that bfs really uses a FIFO frontier (not priority)."
    )
    print("  ok  bfs suboptimal on non-uniform costs (g=10 > optimum 2 -- the lesson)")


def test_dfs_terminates_on_cyclic_graph():
    node, _ = s.dfs(CyclicGraph("A", "G"))   # if this hangs, your DFS lost the explored set
    assert node is not None and node.state == "G", "dfs did not reach the goal"
    print("  ok  dfs terminates on a cyclic graph (explored set does its job)")


def test_ucs_optimal_nonuniform_cost():
    node, _ = s.ucs(TinyGraph("start", "A"))
    assert node is not None
    assert node.g == 2, f"ucs not optimal on non-uniform costs: g={node.g} != 2"
    print("  ok  ucs optimal on non-uniform costs (g=2)")


def test_ids_matches_bfs_solution_length():
    ids_node, _ = s.ids(EightPuzzle(D8))
    bfs_node, _ = s.bfs(EightPuzzle(D8))
    assert ids_node is not None, "ids found no solution"
    assert len(ids_node.path()) == len(bfs_node.path()) == D8_OPTIMAL_LEN, (
        f"ids len {len(ids_node.path())} != bfs len {len(bfs_node.path())} "
        f"(both should be {D8_OPTIMAL_LEN})"
    )
    print(f"  ok  ids matches bfs solution length ({D8_OPTIMAL_LEN}) at O(bd) memory")


TESTS = [
    test_bfs_optimal_uniform_cost,
    test_bfs_suboptimal_nonuniform_cost,
    test_dfs_terminates_on_cyclic_graph,
    test_ucs_optimal_nonuniform_cost,
    test_ids_matches_bfs_solution_length,
]


def main():
    failed = 0
    for t in TESTS:
        try:
            t()
        except NotImplementedError:
            print(f"  --  {t.__name__}: algorithm not implemented yet")
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
