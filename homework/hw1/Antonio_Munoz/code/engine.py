"""engine.py -- instrumented search for HW1.

Same algorithms as search.py / gridworld.py, but every run also reports
max frontier size, wall-clock time and a hard timeout.  The loops are MIRRORS of
the course code (same goal test on expansion, same explored-set / best_g logic,
same tie-break) so expansions are comparable; check_engine.py proves it.

Definitions (also go in PROTOCOL.md):
  expansion    = a node popped from the frontier, not goal, not stale, whose
                 successors are generated (the goal node is not counted).
  max_frontier = largest number of nodes waiting in the frontier. For IDS (no
                 frontier, recursive) it is the deepest recursion reached.
"""
import heapq
import time
from collections import deque


class SearchTimeout(Exception):
    pass


class _N:
    __slots__ = ("state", "parent", "action", "g")

    def __init__(self, state, parent=None, action=None, g=0):
        self.state, self.parent, self.action, self.g = state, parent, action, g


def _path(node):
    out = []
    while node.parent is not None:
        out.append(node.action)
        node = node.parent
    return out[::-1]


def _check(deadline):
    if time.perf_counter() > deadline:
        raise SearchTimeout


def _graph_search(problem, kind, deadline):
    """BFS ('fifo'), DFS ('lifo'), UCS ('priority'). Mirrors search.search()."""
    start = _N(problem.initial)
    if problem.is_goal(start.state):
        return start, 0, 1
    prio = kind == "priority"
    frontier = [] if prio else deque()
    counter = 0
    if prio:
        heapq.heappush(frontier, (0, counter, start))
    else:
        frontier.append(start)
    explored, expansions, max_f = set(), 0, 1
    while frontier:
        if prio:
            node = heapq.heappop(frontier)[2]
        elif kind == "fifo":
            node = frontier.popleft()
        else:
            node = frontier.pop()
        if problem.is_goal(node.state):
            return node, expansions, max_f
        if node.state in explored:
            continue
        _check(deadline)
        explored.add(node.state)
        expansions += 1
        for action in problem.actions(node.state):
            s2 = problem.result(node.state, action)
            if s2 not in explored:
                child = _N(s2, node, action,
                           node.g + problem.step_cost(node.state, action))
                if prio:
                    counter += 1
                    heapq.heappush(frontier, (child.g, counter, child))
                else:
                    frontier.append(child)
        max_f = max(max_f, len(frontier))
    return None, expansions, max_f


def _astar(problem, h, deadline):
    """Mirrors gridworld.astar(): best_g dict, stale-entry skip, FIFO tie-break."""
    start = _N(problem.initial)
    frontier = [(h(problem, start.state), 0, start)]
    best_g = {problem.initial: 0}
    expansions, tiebreak, max_f = 0, 0, 1
    while frontier:
        _, _, node = heapq.heappop(frontier)
        if problem.is_goal(node.state):
            return node, expansions, max_f
        if node.g > best_g.get(node.state, float("inf")):
            continue
        _check(deadline)
        expansions += 1
        for action in problem.actions(node.state):
            s2 = problem.result(node.state, action)
            g2 = node.g + problem.step_cost(node.state, action)
            if g2 < best_g.get(s2, float("inf")):
                best_g[s2] = g2
                tiebreak += 1
                heapq.heappush(frontier, (g2 + h(problem, s2), tiebreak,
                                          _N(s2, node, action, g2)))
        max_f = max(max_f, len(frontier))
    return None, expansions, max_f


def _ids(problem, deadline, max_depth):
    """Mirrors algorithms.ids()/depth_limited(): tree search, skips parent state."""
    total, deepest = 0, 0
    for limit in range(max_depth + 1):
        expansions = 0
        cut = False

        def recur(node, depth, parent_state):
            nonlocal expansions, cut, deepest
            deepest = max(deepest, depth + 1)
            if problem.is_goal(node.state):
                return node
            if depth == limit:
                cut = True
                return None
            _check(deadline)
            expansions += 1
            for action in problem.actions(node.state):
                s2 = problem.result(node.state, action)
                if s2 == parent_state:
                    continue
                child = _N(s2, node, action,
                           node.g + problem.step_cost(node.state, action))
                found = recur(child, depth + 1, node.state)
                if found is not None:
                    return found
            return None

        try:
            found = recur(_N(problem.initial), 0, None)
        except SearchTimeout:
            raise SearchTimeoutWith(total + expansions, deepest)
        total += expansions
        if found is not None:
            return found, total, deepest
        if not cut:
            return None, total, deepest
    return "depth_cap", total, deepest


class SearchTimeoutWith(SearchTimeout):
    def __init__(self, expansions, max_f):
        self.expansions, self.max_f = expansions, max_f


def run(problem, algo, h=None, timeout=10.0, ids_max_depth=60):
    """Run one algorithm on one problem. algo: bfs|dfs|ucs|ids|astar.
    Returns a dict (one CSV row's worth of measurements)."""
    t0 = time.perf_counter()
    deadline = t0 + timeout
    status, node, exp, max_f = "ok", None, 0, 0
    try:
        if algo == "astar":
            node, exp, max_f = _astar(problem, h, deadline)
        elif algo == "ids":
            node, exp, max_f = _ids(problem, deadline, ids_max_depth)
        else:
            kind = {"bfs": "fifo", "dfs": "lifo", "ucs": "priority"}[algo]
            node, exp, max_f = _graph_search(problem, kind, deadline)
    except SearchTimeoutWith as e:
        status, exp, max_f = "timeout", e.expansions, e.max_f
    except SearchTimeout:
        status = "timeout"
    dt = time.perf_counter() - t0
    if status == "ok":
        if node == "depth_cap":
            status, node = "depth_cap", None
        elif node is None:
            status = "no_solution"
    path = _path(node) if (status == "ok" and node is not None) else None
    return {"status": status,
            "cost": node.g if status == "ok" else None,
            "length": len(path) if path is not None else None,
            "expansions": exp, "max_frontier": max_f,
            "time_s": dt, "path": path}
