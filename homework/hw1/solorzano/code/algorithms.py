"""
Algoritmos usados para la comparación clásica vistos en la Week 3 y Week 4: BFS, DFS, UCS, IDS y A*.

También están las heurísticas del 8-puzzle:
- h = 0
- misplaced tiles
- Manhattan
- Manhattan x 3

Para el weighted grid se usan las heurísticas de la Week 4.
"""

import heapq
from math import hypot

from search import Node, search, GOAL
from gridworld import astar as grid_astar, MIN_COST


#Week 3
def bfs(problem):
    return search(problem, "fifo")


def dfs(problem):
    return search(problem, "lifo")


def ucs(problem):
    return search(problem, "priority")


def depth_limited(problem, limit):

    def recursive_dls(node, remaining_limit):

        if problem.is_goal(node.state):
            return node, 0, False

        if remaining_limit == 0:
            return None, 0, True

        expansions = 1
        hit_limit = False

        for action in problem.actions(node.state):
            child_state = problem.result(node.state, action)

            #Se evita solamente el regreso inmediato al padre para no guardar un explored completo
            if node.parent is not None and child_state == node.parent.state:
                continue

            cost = problem.step_cost(node.state, action)

            child = Node(
                child_state,
                parent=node,
                action=action,
                g=node.g + cost
            )

            result_node, child_expansions, child_hit_limit = recursive_dls(
                child,
                remaining_limit - 1
            )

            expansions += child_expansions

            if result_node is not None:
                return result_node, expansions, child_hit_limit

            if child_hit_limit:
                hit_limit = True

        return None, expansions, hit_limit

    start = Node(problem.initial)
    return recursive_dls(start, limit)


def ids(problem, max_depth=40):

    total_expansions = 0

    for limit in range(max_depth + 1):

        node, expansions, hit_limit = depth_limited(problem, limit)
        total_expansions += expansions

        if node is not None:
            return node, total_expansions

        #Si no hubo corte por profundidad, seguir aumentando el límite ya no ayuda
        if not hit_limit:
            return None, total_expansions

    return None, total_expansions


#Week 4
def astar_puzzle(problem, heuristic):

    start = Node(problem.initial)

    #El número extra evita que heapq tenga que comparar objetos Node cuando hay empate
    frontier = [
        (heuristic(start.state), 0, start)
    ]

    best_g = {problem.initial: 0}

    expansions = 0
    tiebreak = 0

    while frontier:

        _, _, node = heapq.heappop(frontier)

        if problem.is_goal(node.state):
            return node, expansions

        #Puede quedar una entrada vieja en el heap después de encontrar un camino mejor
        if node.g > best_g.get(node.state, float("inf")):
            continue

        expansions += 1

        for action in problem.actions(node.state):

            child_state = problem.result(node.state, action)
            new_g = node.g + problem.step_cost(node.state, action)

            if new_g < best_g.get(child_state, float("inf")):

                best_g[child_state] = new_g
                tiebreak += 1

                child = Node(
                    child_state,
                    parent=node,
                    action=action,
                    g=new_g
                )

                new_f = new_g + heuristic(child_state)

                heapq.heappush(
                    frontier,
                    (new_f, tiebreak, child)
                )

    return None, expansions


#Heurísticas del 8-puzzle
def h_zero(state):
    return 0


def h_misplaced(state):

    misplaced = 0

    for i, value in enumerate(state):
        if value != 0 and value != GOAL[i]:
            misplaced += 1

    return misplaced


def manhattan_distance(position_1, position_2):

    row_1, col_1 = divmod(position_1, 3)
    row_2, col_2 = divmod(position_2, 3)

    return abs(row_1 - row_2) + abs(col_1 - col_2)


def h_manhattan(state):

    total = 0

    for current_position, value in enumerate(state):

        if value == 0:
            continue

        goal_position = GOAL.index(value)

        total += manhattan_distance(
            current_position,
            goal_position
        )

    return total


def h_manhattan_x3(state):
    #Se hace inadmisible a propósito para el experimento pedido en el homework
    return 3 * h_manhattan(state)


#Heurísticas del weighted grid
def grid_h_zero(problem, state):
    return 0


def grid_h_manhattan(problem, state):

    goal_row, goal_col = problem.goal
    row, col = state

    return abs(row - goal_row) + abs(col - goal_col)


def grid_h_manhattan_scaled(problem, state):
    #Se escala por el costo mínimo para mantener la cota de la heurística
    return grid_h_manhattan(problem, state) * MIN_COST


def grid_h_euclidean_scaled(problem, state):

    goal_row, goal_col = problem.goal
    row, col = state

    return hypot(
        row - goal_row,
        col - goal_col
    ) * MIN_COST


def astar_grid(problem, heuristic):
    return grid_astar(problem, heuristic)