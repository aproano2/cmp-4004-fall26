from collections import deque
import heapq
import itertools


class Problem:
    """Base class for a search problem."""

    def __init__(self, initial, goal=None):
        self.initial = initial
        self.goal = goal

    def actions(self, state):
        raise NotImplementedError

    def result(self, state, action):
        raise NotImplementedError

    def is_goal(self, state):
        return state == self.goal

    def step_cost(self, state, action):
        return 1


class Node:
    """A node in the search tree."""

    __slots__ = ("state", "parent", "action", "g")

    def __init__(self, state, parent=None, action=None, g=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.g = g

    def path(self):
        """Return the sequence of actions from the root to this node."""
        node = self
        actions = []

        while node.parent is not None:
            actions.append(node.action)
            node = node.parent

        return actions[::-1]

    def __repr__(self):
        return f"Node({self.state}, g={self.g})"


class Frontier:
    """
    FIFO     -> BFS
    LIFO     -> DFS
    Priority -> UCS
    """

    def __init__(self, kind):
        self.kind = kind
        self.counter = itertools.count()

        if kind in ("fifo", "lifo"):
            self.data = deque()
        elif kind == "priority":
            self.data = []
        else:
            raise ValueError(f"Unknown frontier kind: {kind}")

    def push(self, node):
        if self.kind == "priority":
            heapq.heappush(
                self.data,
                (node.g, next(self.counter), node)
            )
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

    def __bool__(self):
        return bool(self.data)


def search(problem, frontier_kind):
    """
    Generic graph search used by BFS, DFS and UCS.

    Returns:
        node: goal Node, or None
        expansions: number of expanded nodes
        max_frontier: largest frontier size observed
    """

    start = Node(problem.initial)

    if problem.is_goal(start.state):
        return start, 0, 1

    frontier = Frontier(frontier_kind)
    frontier.push(start)

    explored = set()

    expansions = 0
    max_frontier = len(frontier)

    while frontier:
        node = frontier.pop()

        # Important: goal test on expansion.
        if problem.is_goal(node.state):
            return node, expansions, max_frontier

        if node.state in explored:
            continue

        explored.add(node.state)
        expansions += 1

        for action in problem.actions(node.state):
            child_state = problem.result(node.state, action)

            if child_state not in explored:
                cost = problem.step_cost(node.state, action)

                child = Node(
                    child_state,
                    parent=node,
                    action=action,
                    g=node.g + cost
                )

                frontier.push(child)

        max_frontier = max(max_frontier, len(frontier))

    return None, expansions, max_frontier


def bfs(problem):
    """Breadth-first search."""
    return search(problem, "fifo")


def dfs(problem):
    """Depth-first search."""
    return search(problem, "lifo")


def ucs(problem):
    """Uniform-cost search."""
    return search(problem, "priority")


def depth_limited(problem, limit):
    """
    Depth-limited search using an explicit LIFO frontier.

    Returns:
        node
        expansions
        max_frontier
        hit_limit
    """

    # Store (node, depth) pairs.
    frontier = [(Node(problem.initial), 0)]

    expansions = 0
    max_frontier = 1
    hit_limit = False

    while frontier:

        node, depth = frontier.pop()

        if problem.is_goal(node.state):
            return node, expansions, max_frontier, hit_limit

        if depth == limit:
            hit_limit = True
            continue

        expansions += 1

        children = []

        for action in problem.actions(node.state):

            child_state = problem.result(
                node.state,
                action
            )

            # Avoid cycles along the current path.
            ancestor = node
            cycle = False

            while ancestor is not None:
                if ancestor.state == child_state:
                    cycle = True
                    break

                ancestor = ancestor.parent

            if cycle:
                continue

            cost = problem.step_cost(
                node.state,
                action
            )

            child = Node(
                child_state,
                parent=node,
                action=action,
                g=node.g + cost
            )

            children.append(
                (child, depth + 1)
            )

        # Reverse so that DFS explores actions in the
        # same order returned by problem.actions().
        frontier.extend(reversed(children))

        max_frontier = max(
            max_frontier,
            len(frontier)
        )

    return None, expansions, max_frontier, hit_limit


def ids(problem, max_depth=40):
    """Iterative deepening search."""

    total_expansions = 0
    max_frontier = 1

    for limit in range(max_depth + 1):

        node, expansions, frontier_size, hit_limit = depth_limited(
            problem,
            limit
        )

        total_expansions += expansions
        max_frontier = max(max_frontier, frontier_size)

        if node is not None:
            return node, total_expansions, max_frontier

        if not hit_limit:
            return None, total_expansions, max_frontier

    return None, total_expansions, max_frontier

def astar(problem, heuristic):
    """
    A* graph search.

    Priority:
        f(n) = g(n) + h(n)

    Returns:
        node: goal Node, or None
        expansions: number of expanded nodes
        max_frontier: largest frontier size observed
    """

    start = Node(problem.initial)

    if problem.is_goal(start.state):
        return start, 0, 1

    frontier = []
    counter = itertools.count()

    # (f, tie-breaker, node)
    heapq.heappush(
        frontier,
        (
            heuristic(start.state),
            next(counter),
            start,
        )
    )

    # Best known cost to each state.
    best_g = {start.state: 0}

    expansions = 0
    max_frontier = 1

    while frontier:

        _, _, node = heapq.heappop(frontier)

        # Ignore stale entries.
        if node.g != best_g.get(node.state):
            continue

        if problem.is_goal(node.state):
            return node, expansions, max_frontier

        expansions += 1

        for action in problem.actions(node.state):

            child_state = problem.result(
                node.state,
                action
            )

            new_g = (
                node.g
                + problem.step_cost(node.state, action)
            )

            # Only keep this path if it improves the
            # best known cost to child_state.
            if new_g < best_g.get(child_state, float("inf")):

                best_g[child_state] = new_g

                child = Node(
                    child_state,
                    parent=node,
                    action=action,
                    g=new_g
                )

                f = new_g + heuristic(child_state)

                heapq.heappush(
                    frontier,
                    (
                        f,
                        next(counter),
                        child,
                    )
                )

        max_frontier = max(
            max_frontier,
            len(frontier)
        )

    return None, expansions, max_frontier