"""Week 3 studio — the shared search engine (GIVEN to you; do not modify).

This is the generic search from the Session-3A notebook, unchanged: one
``search()`` loop parameterized by a *frontier discipline*, plus the five-component
``Problem`` interface every week 3–9 talks to.

    problem.actions(state)        -> iterable of legal actions
    problem.result(state, action) -> next state
    problem.is_goal(state)        -> bool
    problem.step_cost(s, action)  -> cost of applying `action` in state `s`
    search(problem, frontier_kind)-> (goal_node, expansions)  or  (None, expansions)
    node.path()                   -> list of actions; node.g -> path cost

⚠️  The same interface is reused verbatim by the week-4 studio (A* is a 10-line
diff) and the week-9 planner. If you break it here, it stays broken. Do not edit
this file — you write the algorithms and the problem in ``starter.py``.

Two load-bearing details in ``search()`` (both cost points in Duel 1 if skipped):
  1. the goal test fires on EXPANSION, not on generation — testing at generation
     time breaks UCS optimality (see ``TinyGraph`` below);
  2. ``expansions`` is instrumented from line one — it is the only currency in
     which these four algorithms can be compared (scorecard axis 3).
"""
from collections import deque
import heapq
import itertools
import json
from pathlib import Path


class Problem:
    """The five components: initial state, actions, transition, goal test, cost."""

    def __init__(self, initial, goal=None):
        self.initial, self.goal = initial, goal

    def actions(self, state):
        raise NotImplementedError

    def result(self, state, action):
        raise NotImplementedError

    def is_goal(self, state):
        return state == self.goal

    def step_cost(self, state, action):
        return 1


class Node:
    __slots__ = ("state", "parent", "action", "g")

    def __init__(self, state, parent=None, action=None, g=0):
        self.state, self.parent, self.action, self.g = state, parent, action, g

    def path(self):
        node, out = self, []
        while node.parent is not None:
            out.append(node.action)
            node = node.parent
        return out[::-1]

    def __repr__(self):
        return f"Node({self.state}, g={self.g})"


class Frontier:
    """FIFO -> BFS.  LIFO -> DFS.  Priority by g -> UCS.

    The *only* thing that differs between BFS, DFS, and UCS is the data structure
    that decides which node comes out next. Same search loop; three disciplines.
    """

    def __init__(self, kind):
        self.kind = kind
        self.counter = itertools.count()
        if kind in ("fifo", "lifo"):
            self.data = deque()
        elif kind == "priority":
            self.data = []
        else:
            raise ValueError(kind)

    def push(self, node):
        if self.kind == "priority":
            heapq.heappush(self.data, (node.g, next(self.counter), node))
        else:
            self.data.append(node)

    def pop(self):
        if self.kind == "priority":
            return heapq.heappop(self.data)[2]
        if self.kind == "fifo":
            return self.data.popleft()
        return self.data.pop()

    def __len__(self):
        return len(self.data)


def search(problem, frontier_kind):
    """Generic graph search. Returns (goal_node, expansions).

    ``frontier_kind`` is one of ``"fifo"`` (BFS), ``"lifo"`` (DFS),
    ``"priority"`` (UCS). This is the whole trick of the week.
    """
    start = Node(problem.initial)
    if problem.is_goal(start.state):
        return start, 0

    frontier = Frontier(frontier_kind)
    frontier.push(start)
    explored = set()
    expansions = 0                       # instrument from line one

    while frontier:
        node = frontier.pop()
        if problem.is_goal(node.state):  # goal test on EXPANSION, not generation
            return node, expansions
        if node.state in explored:
            continue
        explored.add(node.state)
        expansions += 1
        for action in problem.actions(node.state):
            child_state = problem.result(node.state, action)
            if child_state not in explored:
                cost = problem.step_cost(node.state, action)
                frontier.push(Node(child_state, node, action, node.g + cost))
    return None, expansions


# ---- Fixtures from the notebook (GIVEN; the tests import these) -------------

class TinyGraph(Problem):
    """The 3-node non-uniform-cost graph from the notebook. The optimal path to
    ``A`` costs 2 (start -> B -> A), but the *fewest-edges* path costs 10
    (start -> A). BFS counts edges, so BFS returns the cost-10 path — that is why
    ``test_bfs_suboptimal_nonuniform_cost`` asserts a wrong answer."""

    EDGES = {"start": [("A", 10), ("B", 1)], "B": [("A", 1)], "A": []}

    def actions(self, state):
        return [dst for dst, _ in self.EDGES[state]]

    def result(self, state, action):
        return action

    def step_cost(self, state, action):
        return dict(self.EDGES[state])[action]


GOAL = (1, 2, 3, 4, 5, 6, 7, 8, 0)


class EightPuzzle(Problem):
    """State is a 9-tuple; ``0`` is the blank. We chose a flat tuple so states are
    hashable and comparable in one operation — formulation is a design decision."""

    MOVES = {0: (1, 3), 1: (0, 2, 4), 2: (1, 5),
             3: (0, 4, 6), 4: (1, 3, 5, 7), 5: (2, 4, 8),
             6: (3, 7), 7: (4, 6, 8), 8: (5, 7)}

    def __init__(self, initial, goal=GOAL):
        super().__init__(initial, goal)

    def actions(self, state):
        return self.MOVES[state.index(0)]

    def result(self, state, action):
        s = list(state)
        b = state.index(0)
        s[b], s[action] = s[action], s[b]
        return tuple(s)


def show(state):
    for r in range(0, 9, 3):
        print(" ".join("_" if v == 0 else str(v) for v in state[r:r + 3]))


# Depths VERIFIED by exhaustive BFS from the goal (see _generate_instances.py).
# Do not trust hand-labelled puzzle depths -- including these.
D2  = (1, 2, 3, 4, 5, 6, 0, 7, 8)      # optimal 2
D8  = (0, 4, 2, 5, 1, 3, 7, 8, 6)      # optimal 8
D12 = (5, 4, 2, 7, 0, 3, 8, 1, 6)      # optimal 12
D16 = (7, 5, 2, 4, 0, 3, 8, 1, 6)      # optimal 16  <- week 4 uses this one


# ---- instance loading -------------------------------------------------------

def load_instances(path=None):
    """Load the 8-puzzle instance bank as {depth: [state, ...]} where each state
    is a 9-tuple. See instances.json (generated with a fixed seed; depths verified
    by exhaustive BFS from the goal)."""
    path = Path(path or Path(__file__).with_name("instances.json"))
    data = json.loads(path.read_text())
    return {int(k): [tuple(s) for s in v] for k, v in data["instances"].items()}
