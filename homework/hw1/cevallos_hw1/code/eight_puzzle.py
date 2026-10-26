from search import Problem


GOAL_STATE = (
    1, 2, 3,
    4, 5, 6,
    7, 8, 0
)


class EightPuzzle(Problem):
    """
    Standard 8-puzzle.

    State representation:
        tuple of 9 integers

    Example:
        (1, 2, 3,
         4, 0, 6,
         7, 5, 8)

    0 represents the blank tile.
    """

    def __init__(self, initial, goal=GOAL_STATE):
        super().__init__(initial, goal)

    def actions(self, state):
        """Return legal moves for the blank tile."""

        blank = state.index(0)
        row, col = divmod(blank, 3)

        moves = []

        if row > 0:
            moves.append("UP")

        if row < 2:
            moves.append("DOWN")

        if col > 0:
            moves.append("LEFT")

        if col < 2:
            moves.append("RIGHT")

        return moves

    def result(self, state, action):
        """Return the state produced by moving the blank."""

        blank = state.index(0)
        row, col = divmod(blank, 3)

        if action == "UP":
            new_row, new_col = row - 1, col

        elif action == "DOWN":
            new_row, new_col = row + 1, col

        elif action == "LEFT":
            new_row, new_col = row, col - 1

        elif action == "RIGHT":
            new_row, new_col = row, col + 1

        else:
            raise ValueError(f"Unknown action: {action}")

        target = new_row * 3 + new_col

        new_state = list(state)

        new_state[blank], new_state[target] = (
            new_state[target],
            new_state[blank],
        )

        return tuple(new_state)

    def step_cost(self, state, action):
        """Every move in the 8-puzzle costs 1."""
        return 1