"""Week 3 studio — starter (formulation + the four algorithms).

You fill in three things. Run ``python3 test_search.py`` as you go.

  Task 1  MissionariesAndCannibals  -- formulate the five components (graded).
  Task 2  bfs / dfs / ucs / ids     -- four algorithms, one search loop.
  Task 3  the measurement harness    -- run all four on the 8-puzzle bank.

The provided tests include ``test_bfs_suboptimal_nonuniform_cost``, which asserts
that BFS returns a NON-optimal path. That is not a broken test: BFS's optimality
claim has a condition (uniform step costs), and this instance violates it. Watching
a guarantee fail once is how you learn the guarantee is real.
"""
from search import Problem, Node, search


# ---- Task 1: formulate missionaries & cannibals -----------------------------
# Three missionaries, three cannibals, one boat that carries 1 or 2 and cannot
# cross empty. If cannibals ever outnumber missionaries on EITHER bank (and a
# missionary is present), the missionaries are eaten. Get everyone to the far
# bank. Formulation is a design decision -- you must be able to defend whether
# illegal states are excluded by ``actions()`` or by ``result()``.
#
# Suggested state: (m_left, c_left, boat_side) where boat_side is 0=left, 1=right
# and m_left/c_left count the people on the LEFT bank. Initial (3, 3, 0),
# goal (0, 0, 1). But this is YOUR call -- justify it in the demo.

class MissionariesAndCannibals(Problem):
    def __init__(self):
        # TODO: set self.initial and self.goal (call super().__init__)
        raise NotImplementedError

    def actions(self, state):
        # TODO: return the legal boat-loads from `state`. Decide here or in
        # result()/is_valid() where the "cannibals outnumber missionaries" rule
        # is enforced -- and be ready to defend the choice.
        raise NotImplementedError

    def result(self, state, action):
        # TODO: apply `action`, flipping the boat side.
        raise NotImplementedError

    def is_goal(self, state):
        # TODO
        raise NotImplementedError


# ---- Task 2: the four algorithms -- one search loop, four frontiers ---------
# search(problem, frontier_kind) is GIVEN in search.py. Three of these are one
# line: pick the frontier discipline. IDS is the interesting one -- it does NOT
# use search(); you write a depth-limited DFS and iterate the limit, buying BFS's
# completeness at DFS's O(bd) memory by re-doing the shallow work.

def bfs(problem):
    """Breadth-first search. Complete; optimal only when step costs are uniform."""
    # TODO: return search(problem, ...)
    raise NotImplementedError


def dfs(problem):
    """Depth-first (graph) search. The explored set is what makes it terminate on
    cyclic graphs -- do not remove it. Not optimal."""
    # TODO
    raise NotImplementedError


def ucs(problem):
    """Uniform-cost search. Optimal for any non-negative step costs."""
    # TODO
    raise NotImplementedError


def depth_limited(problem, limit):
    """Recursive tree search to a fixed depth.

    Return (node, expansions, hit_limit): ``node`` is the goal Node or None;
    ``expansions`` counts expanded nodes; ``hit_limit`` is True iff the search was
    cut off by the depth limit (as opposed to exhausting the subtree). The
    hit_limit flag is what lets ids() know whether deepening further can help.

    Hint: skip the immediate parent state to avoid trivial 2-cycles at no memory
    cost, then recurse with limit-1.
    """
    # TODO
    raise NotImplementedError


def ids(problem, max_depth=40):
    """Iterative deepening: call depth_limited with limit = 0, 1, 2, ... until a
    goal is found. Return (node, total_expansions). If a level reports it was NOT
    cut off and found nothing, the space is exhausted -- return (None, total)."""
    # TODO
    raise NotImplementedError


# ---- Task 3: measurement (fill in after Task 2 passes) ----------------------
def measure(bank=None):
    """Run all four on the 8-puzzle bank and return rows of
    (depth, algorithm, expansions, solution_length). Then plot expansions vs.
    depth on a LOG y-axis -- that log-scale plot is the deliverable."""
    from search import load_instances, EightPuzzle
    bank = bank or load_instances()
    rows = []
    for depth in sorted(bank):
        for state in bank[depth]:
            p = EightPuzzle(state)
            for name, algo in [("BFS", bfs), ("DFS", dfs),
                               ("UCS", ucs), ("IDS", ids)]:
                node, exp = algo(p)
                rows.append((depth, name, exp, len(node.path())))
    return rows


if __name__ == "__main__":
    # Smoke test: solve the depth-8 instance with each algorithm you've filled in.
    from search import EightPuzzle, D8
    p = EightPuzzle(D8)
    for name, algo in [("bfs", bfs), ("dfs", dfs), ("ucs", ucs), ("ids", ids)]:
        try:
            node, exp = algo(p)
        except NotImplementedError:
            print(f"  {name:<5} not implemented yet")
            continue
        print(f"  {name:<5} len={len(node.path()):>4}  expansions={exp:,}")
