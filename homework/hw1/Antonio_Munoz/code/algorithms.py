"""Week 3 studio — REFERENCE SOLUTION (instructor-only).

A filled-in copy of ``starter.py``: identical function names and signatures, so
the *provided* ``test_search.py`` passes when this module is imported in place of
``starter``. Verify with ``studios/_verify_solutions.py`` (which aliases this file
to the name ``starter`` and runs the unmodified test).

DO NOT ship this to students — it is excluded via ``studios/.gitignore``. The
teaching walkthrough lives in ``solution.ipynb`` (which imports this file rather
than re-pasting it, so the two never drift).
"""
from search import Problem, Node, search


# ---- Task 1: formulate missionaries & cannibals -----------------------------
# State: (m_left, c_left, boat_side) with boat_side 0=left, 1=right and
# m_left/c_left counting people on the LEFT bank. Initial (3, 3, 0), goal
# (0, 0, 1). Design decision (defend it in the demo): we enforce the
# "cannibals never outnumber missionaries on either bank" rule inside
# ``actions()`` — a state is only reachable if it is legal — so ``result()``
# stays a pure transition and the search never touches an eaten-missionary state.

# Boat carries 1 or 2 people and is never empty.
_BOAT_LOADS = [(1, 0), (2, 0), (0, 1), (0, 2), (1, 1)]


class MissionariesAndCannibals(Problem):
    def __init__(self):
        super().__init__((3, 3, 0), (0, 0, 1))

    def _legal(self, state):
        """No bank may have cannibals outnumbering missionaries when at least one
        missionary stands there. Also enforce the 0..3 population bounds."""
        m_left, c_left, _ = state
        if not (0 <= m_left <= 3 and 0 <= c_left <= 3):
            return False
        m_right, c_right = 3 - m_left, 3 - c_left
        if m_left > 0 and c_left > m_left:
            return False
        if m_right > 0 and c_right > m_right:
            return False
        return True

    def actions(self, state):
        m_left, c_left, boat = state
        legal = []
        for dm, dc in _BOAT_LOADS:
            if boat == 0:                      # boat on left → carry people right
                if dm <= m_left and dc <= c_left:
                    nxt = (m_left - dm, c_left - dc, 1)
                    if self._legal(nxt):
                        legal.append((dm, dc))
            else:                              # boat on right → carry people left
                m_right, c_right = 3 - m_left, 3 - c_left
                if dm <= m_right and dc <= c_right:
                    nxt = (m_left + dm, c_left + dc, 0)
                    if self._legal(nxt):
                        legal.append((dm, dc))
        return legal

    def result(self, state, action):
        m_left, c_left, boat = state
        dm, dc = action
        if boat == 0:
            return (m_left - dm, c_left - dc, 1)
        return (m_left + dm, c_left + dc, 0)

    def is_goal(self, state):
        return state == self.goal


# ---- Task 2: the four algorithms -- one search loop, four frontiers ---------

def bfs(problem):
    """Breadth-first search. Complete; optimal only when step costs are uniform."""
    return search(problem, "fifo")


def dfs(problem):
    """Depth-first (graph) search. The explored set in ``search()`` is what makes
    it terminate on cyclic graphs. Not optimal."""
    return search(problem, "lifo")


def ucs(problem):
    """Uniform-cost search. Optimal for any non-negative step costs."""
    return search(problem, "priority")


def depth_limited(problem, limit):
    """Recursive tree search to a fixed depth.

    Returns ``(node, expansions, hit_limit)``: ``node`` is the goal Node or None;
    ``expansions`` counts expanded nodes; ``hit_limit`` is True iff the search was
    cut off by the depth limit (rather than exhausting the subtree). That flag is
    what lets ``ids`` know whether deepening further can still help.

    We skip the immediate parent state to avoid trivial 2-cycles at no memory
    cost (this is *tree* search — no explored set — so the depth bound is what
    guarantees termination).
    """
    expansions = 0

    def recur(node, limit, parent_state):
        nonlocal expansions
        if problem.is_goal(node.state):
            return node, False             # found — this branch was not cut off
        if limit == 0:
            return None, True              # cut off by the depth bound
        expansions += 1
        cutoff = False
        for action in problem.actions(node.state):
            child_state = problem.result(node.state, action)
            if child_state == parent_state:
                continue                   # don't bounce straight back
            child = Node(child_state, node, action,
                         node.g + problem.step_cost(node.state, action))
            found, was_cut = recur(child, limit - 1, node.state)
            if found is not None:
                return found, was_cut
            if was_cut:
                cutoff = True
        return None, cutoff

    root = Node(problem.initial)
    node, hit_limit = recur(root, limit, None)
    return node, expansions, hit_limit


def ids(problem, max_depth=40):
    """Iterative deepening: call ``depth_limited`` with limit = 0, 1, 2, ... until
    a goal is found. Returns ``(node, total_expansions)``. If a level reports it
    was NOT cut off and found nothing, the space is exhausted → ``(None, total)``.
    """
    total = 0
    for limit in range(max_depth + 1):
        node, expansions, hit_limit = depth_limited(problem, limit)
        total += expansions
        if node is not None:
            return node, total
        if not hit_limit:                  # nothing left below → exhausted
            return None, total
    return None, total


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
    from search import EightPuzzle, D8
    p = EightPuzzle(D8)
    for name, algo in [("bfs", bfs), ("dfs", dfs), ("ucs", ucs), ("ids", ids)]:
        node, exp = algo(p)
        print(f"  {name:<5} len={len(node.path()):>4}  expansions={exp:,}")
