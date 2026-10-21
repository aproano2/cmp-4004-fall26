"""Duel 1 / Part 1 — the instrumented search engine.

The studio engines (``search.search`` and ``gridworld.astar``) are kept verbatim
in this folder as *reference oracles*, but they cannot be benchmarked directly:
neither records the maximum frontier size nor honours a hard wall-clock
deadline. This module is the same algorithm with three additions:

  1. one ``Result`` record per run — status, cost, length, expansions,
     generated, max_frontier, seconds;
  2. a ``deadline`` checked inside the loop. A run that runs out of time returns
     ``status == "timeout"`` — it is never reported as a failure to solve;
  3. four frontier disciplines behind one loop: ``"fifo"`` (BFS), ``"lifo"``
     (DFS), ``"ucs"`` (priority by g), ``"astar"`` (priority by g + h).

Guarantees carried over from the course engines:

  * the goal test fires on **expansion**, not generation — testing at generation
    time breaks UCS/A* optimality on non-uniform costs;
  * ``search(p, "ucs")`` is semantically identical to
    ``search.search(p, "priority")``;
  * ``search(p, "astar", h)`` is semantically identical to
    ``gridworld.astar(p, h)`` — ``best_g`` stale-entry skipping, a tie-break
    counter, no closed set;
  * ``ids()`` is tree search with a parent-skip, exactly like the week-3
    ``starter.py``, so expansion counts stay comparable with the studio work.

``test_engine.py`` asserts the three equivalences above over all 80 instances of
the two banks; this file is not trusted on its own.
"""

from __future__ import annotations

import heapq
import time
from collections import deque
from dataclasses import dataclass
from itertools import count

from search import Node

SOLVED = "solved"
TIMEOUT = "timeout"
EXHAUSTED = "exhausted"

# A goal is always found within 31 moves on the 8-puzzle and 30 on an n x n grid,
# so a depth bound of 64 can never be the reason a run fails. If IDS ever hits
# this bound the status would be "exhausted", which would be a bug worth seeing.
IDS_MAX_DEPTH = 64


@dataclass
class Result:
    """Everything the protocol asks for, measured in one place."""

    status: str = EXHAUSTED
    node: Node | None = None
    expansions: int = 0
    generated: int = 0
    max_frontier: int = 0
    seconds: float = 0.0
    cutoff: bool = False          # depth-limited search only: hit the bound?
    depth_limit: int | None = None

    def __iter__(self):
        """``node, expansions = bfs(problem)`` — keeps the week-3 test-suite
        interface (``test_search.py`` unpacks exactly two values)."""
        yield self.node
        yield self.expansions

    @property
    def solved(self) -> bool:
        return self.status == SOLVED

    @property
    def cost(self):
        return self.node.g if self.node is not None else None

    @property
    def length(self):
        return len(self.node.path()) if self.node is not None else None


def _finish(status: str, node, r: Result, t0: float) -> Result:
    r.status = status
    r.node = node
    r.seconds = time.perf_counter() - t0
    return r


def search(problem, discipline, h=None, timeout=None) -> Result:
    """Generic graph search. ``discipline`` is one of
    ``"fifo" | "lifo" | "ucs" | "astar"``.

    ``timeout`` is a hard wall-clock budget in seconds for this single call
    (``None`` = unlimited). The deadline is checked once per loop iteration,
    which costs ~100 ns against a per-node cost of microseconds.
    """
    if discipline not in ("fifo", "lifo", "ucs", "astar"):
        raise ValueError(discipline)
    if discipline == "astar" and h is None:
        raise ValueError("the 'astar' discipline requires a heuristic h")

    deadline = None if timeout is None else time.monotonic() + timeout
    t0 = time.perf_counter()
    r = Result()

    start = Node(problem.initial)
    if problem.is_goal(start.state):
        return _finish(SOLVED, start, r, t0)

    # ---- A*: priority by g + h, best_g stale-entry skipping -----------------
    if discipline == "astar":
        frontier = [(h(problem, start.state), 0, start)]
        best_g = {start.state: 0}
        tiebreak = 0
        r.max_frontier = 1
        while frontier:
            if deadline is not None and time.monotonic() > deadline:
                return _finish(TIMEOUT, None, r, t0)
            _, _, node = heapq.heappop(frontier)
            if problem.is_goal(node.state):          # goal test on EXPANSION
                return _finish(SOLVED, node, r, t0)
            if node.g > best_g.get(node.state, float("inf")):
                continue                              # stale entry
            r.expansions += 1
            for action in problem.actions(node.state):
                s2 = problem.result(node.state, action)
                g2 = node.g + problem.step_cost(node.state, action)
                if g2 < best_g.get(s2, float("inf")):
                    best_g[s2] = g2
                    tiebreak += 1
                    heapq.heappush(frontier,
                                   (g2 + h(problem, s2), tiebreak,
                                    Node(s2, node, action, g2)))
                    r.generated += 1
                    if len(frontier) > r.max_frontier:
                        r.max_frontier = len(frontier)
        return _finish(EXHAUSTED, None, r, t0)

    # ---- BFS / DFS / UCS: one loop, three disciplines -----------------------
    counter = count()
    if discipline == "ucs":
        data = []

        def push(node):
            heapq.heappush(data, (node.g, next(counter), node))

        def pop():
            return heapq.heappop(data)[2]
    else:
        data = deque()
        push = data.append
        pop = data.popleft if discipline == "fifo" else data.pop

    push(start)
    r.max_frontier = 1
    explored = set()
    while data:
        if deadline is not None and time.monotonic() > deadline:
            return _finish(TIMEOUT, None, r, t0)
        node = pop()
        if problem.is_goal(node.state):              # goal test on EXPANSION
            return _finish(SOLVED, node, r, t0)
        if node.state in explored:
            continue
        explored.add(node.state)
        r.expansions += 1
        for action in problem.actions(node.state):
            s2 = problem.result(node.state, action)
            if s2 in explored:
                continue
            push(Node(s2, node, action, node.g + problem.step_cost(node.state, action)))
            r.generated += 1
            if len(data) > r.max_frontier:
                r.max_frontier = len(data)
    return _finish(EXHAUSTED, None, r, t0)


class _Timeout(Exception):
    pass


def depth_limited(problem, limit, timeout=None) -> Result:
    """One depth-limited DFS (tree search, parent-skip only).

    Returns ``status == "solved"``, or ``cutoff=True`` when the bound cut the
    search off (so deeper is worth trying), or ``cutoff=False`` when the subtree
    was genuinely exhausted.

    Frontier size for a depth-first search is the call stack, which never
    exceeds ``limit + 1`` — that is what ``max_frontier`` reports here, and it
    is why IDS costs O(bd) memory (scorecard axis 3).
    """
    deadline = None if timeout is None else time.monotonic() + timeout
    t0 = time.perf_counter()
    r = Result(cutoff=False, depth_limit=limit)
    r.max_frontier = 1

    def recur(node, remaining, parent_state, depth):
        if deadline is not None and time.monotonic() > deadline:
            raise _Timeout
        # The frame itself counts, including the goal/cutoff frame — so a search
        # that runs to the bound reports limit + 1 frames (root .. limit).
        if depth + 1 > r.max_frontier:
            r.max_frontier = depth + 1
        if problem.is_goal(node.state):
            return node, False
        if remaining == 0:
            return None, True                      # cut off by the bound
        r.expansions += 1                          # same counting as week 3
        cutoff = False
        for action in problem.actions(node.state):
            s2 = problem.result(node.state, action)
            if s2 == parent_state:
                continue                           # no 2-cycles in tree search
            r.generated += 1
            child = Node(s2, node, action, node.g + problem.step_cost(node.state, action))
            found, cut = recur(child, remaining - 1, node.state, depth + 1)
            if found is not None:
                return found, False
            cutoff = cutoff or cut
        return None, cutoff

    try:
        found, hit = recur(Node(problem.initial), limit, None, 0)
    except _Timeout:
        return _finish(TIMEOUT, None, r, t0)
    if found is not None:
        return _finish(SOLVED, found, r, t0)
    r.cutoff = hit
    return _finish(EXHAUSTED, None, r, t0)


def ids(problem, timeout=None, max_depth=IDS_MAX_DEPTH) -> Result:
    """Iterative deepening: limits 0, 1, 2, ... until a goal appears.

    ``timeout`` is a *total* budget for the whole iteration, not per limit.
    The cumulative expansion/generated counts are what the protocol compares
    against BFS; ``max_frontier`` is the largest stack seen across iterations.
    """
    deadline = None if timeout is None else time.monotonic() + timeout
    t0 = time.perf_counter()
    total = Result()
    for limit in range(max_depth + 1):
        remaining = None
        if deadline is not None:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return _finish(TIMEOUT, None, total, t0)
        sub = depth_limited(problem, limit, timeout=remaining)
        total.expansions += sub.expansions
        total.generated += sub.generated
        total.max_frontier = max(total.max_frontier, sub.max_frontier)
        total.cutoff = sub.cutoff
        total.depth_limit = limit
        if sub.status == TIMEOUT:
            return _finish(TIMEOUT, None, total, t0)
        if sub.solved:
            return _finish(SOLVED, sub.node, total, t0)
        if not sub.cutoff:                          # space exhausted below
            return _finish(EXHAUSTED, None, total, t0)
    return _finish(EXHAUSTED, None, total, t0)
