from eight_puzzle import GOAL_STATE


def h_zero(state, goal=GOAL_STATE):
    """
    Zero heuristic.

    A* with h=0 behaves like UCS.
    """
    return 0


def h_misplaced(state, goal=GOAL_STATE):
    """
    Misplaced-tiles heuristic.

    Counts how many numbered tiles are not in their goal position.
    The blank tile (0) is ignored.
    """
    return sum(
        1
        for i, tile in enumerate(state)
        if tile != 0 and tile != goal[i]
    )


def h_manhattan(state, goal=GOAL_STATE):
    """
    Manhattan-distance heuristic.

    For every numbered tile, compute the horizontal + vertical
    distance between its current position and its goal position.
    The blank tile (0) is ignored.
    """

    total = 0

    # Map each tile to its position in the goal state.
    goal_positions = {
        tile: divmod(index, 3)
        for index, tile in enumerate(goal)
    }

    for index, tile in enumerate(state):

        if tile == 0:
            continue

        current_row, current_col = divmod(index, 3)
        goal_row, goal_col = goal_positions[tile]

        total += (
            abs(current_row - goal_row)
            + abs(current_col - goal_col)
        )

    return total


def h_manhattan_x3(state, goal=GOAL_STATE):
    """
    Deliberately inadmissible heuristic.

    Used to measure the speed/solution-quality tradeoff
    required by the homework.
    """
    return 3 * h_manhattan(state, goal)

def effective_bf(expansions, depth, tolerance=1e-6):
    """
    Compute the effective branching factor b*.

    Solves:
        N + 1 = 1 + b + b^2 + ... + b^d

    where:
        N = node expansions
        d = solution depth

    Uses binary search.
    """

    if depth == 0:
        return 0.0

    if expansions <= 0:
        return 0.0

    target = expansions + 1

    def total_nodes(b):
        return sum(
            b ** i
            for i in range(depth + 1)
        )

    low = 0.0
    high = max(2.0, float(expansions))

    while high - low > tolerance:

        mid = (low + high) / 2

        if total_nodes(mid) < target:
            low = mid
        else:
            high = mid

    return (low + high) / 2