"""
Benchmark de la Parte 1

Se prueban los algoritmos en:
- 8-puzzle
- weighted grid

Los resultados se guardan en: results/classical_results.csv
"""

import argparse
import csv
import heapq
import json
import multiprocessing
import time
from pathlib import Path

from search import Node, Frontier, EightPuzzle
from gridworld import GridProblem

from algorithms import (
    h_zero,
    h_misplaced,
    h_manhattan,
    h_manhattan_x3,
    grid_h_zero,
    grid_h_manhattan_scaled,
    grid_h_euclidean_scaled,
)


#Archivos usados en el experimento
CODE_DIR = Path(__file__).resolve().parent
HW1_DIR = CODE_DIR.parent

PUZZLE_INSTANCES = CODE_DIR / "instances_8puzzle.json"
GRID_INSTANCES = CODE_DIR / "instances_grid.json"
RESULTS_FILE = HW1_DIR / "results" / "classical_results.csv"


def load_puzzle_instances():

    with open(PUZZLE_INSTANCES, "r", encoding="utf-8") as file:
        data = json.load(file)

    bank = {}

    for depth, states in data["instances"].items():
        bank[int(depth)] = [
            tuple(state)
            for state in states
        ]

    return bank


def load_grid_instances():

    with open(GRID_INSTANCES, "r", encoding="utf-8") as file:
        data = json.load(file)

    return {
        int(size): grids
        for size, grids in data["instances"].items()
    }


#Versión de search() que también registra el máximo de la frontera
def search_with_metrics(problem, frontier_kind):

    start = Node(problem.initial)

    if problem.is_goal(start.state):
        return start, 0, 1

    frontier = Frontier(frontier_kind)
    frontier.push(start)

    explored = set()

    expansions = 0
    max_frontier = 1

    while len(frontier) > 0:

        node = frontier.pop()

        #Se mantiene el goal test al sacar el nodo de la frontera
        if problem.is_goal(node.state):
            return node, expansions, max_frontier

        if node.state in explored:
            continue

        explored.add(node.state)
        expansions += 1

        for action in problem.actions(node.state):

            child_state = problem.result(
                node.state,
                action
            )

            if child_state not in explored:

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

                frontier.push(child)

        max_frontier = max(
            max_frontier,
            len(frontier)
        )

    return None, expansions, max_frontier


#IDS separado para poder medir la frontera
def depth_limited_with_metrics(problem, limit):

    start = Node(problem.initial)
    frontier = [(start, 0)]

    expansions = 0
    max_frontier = 1
    hit_limit = False

    while frontier:

        node, depth = frontier.pop()

        if problem.is_goal(node.state):
            return (
                node,
                expansions,
                hit_limit,
                max_frontier
            )

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

            #Se evita solo el regreso inmediato al padre, igual que en IDS de Week 3
            if (
                node.parent is not None
                and child_state == node.parent.state
            ):
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

            children.append(child)

        #Se agregan al revés para conservar el orden al usar la pila
        for child in reversed(children):
            frontier.append(
                (child, depth + 1)
            )

        max_frontier = max(
            max_frontier,
            len(frontier)
        )

    return (
        None,
        expansions,
        hit_limit,
        max_frontier
    )


def ids_with_metrics(problem, max_depth=40):

    total_expansions = 0
    max_frontier = 1

    for limit in range(max_depth + 1):
        node, expansions, hit_limit, frontier_size = depth_limited_with_metrics(problem, limit)

        total_expansions += expansions

        max_frontier = max(
            max_frontier,
            frontier_size
        )

        if node is not None:
            return (
                node,
                total_expansions,
                max_frontier
            )

        #Si no hubo corte por profundidad, no tiene sentido aumentar más el límite
        if not hit_limit:
            return (
                None,
                total_expansions,
                max_frontier
            )

    return (
        None,
        total_expansions,
        max_frontier
    )


#A* con las métricas adicionales del homework
def astar_with_metrics(problem, heuristic):

    start = Node(problem.initial)

    frontier = [
        (
            heuristic(problem, start.state),
            0,
            start
        )
    ]

    best_g = {
        problem.initial: 0
    }

    expansions = 0
    max_frontier = 1
    tiebreak = 0

    while frontier:

        _, _, node = heapq.heappop(frontier)

        if problem.is_goal(node.state):
            return (
                node,
                expansions,
                max_frontier
            )

        #El heap puede mantener una entrada vieja después de encontrar un mejor camino
        if node.g > best_g.get(
            node.state,
            float("inf")
        ):
            continue

        expansions += 1

        for action in problem.actions(node.state):

            child_state = problem.result(
                node.state,
                action
            )

            new_g = (
                node.g
                + problem.step_cost(
                    node.state,
                    action
                )
            )

            if new_g < best_g.get(
                child_state,
                float("inf")
            ):

                best_g[child_state] = new_g
                tiebreak += 1

                child = Node(
                    child_state,
                    parent=node,
                    action=action,
                    g=new_g
                )

                new_f = (
                    new_g
                    + heuristic(
                        problem,
                        child_state
                    )
                )

                heapq.heappush(
                    frontier,
                    (
                        new_f,
                        tiebreak,
                        child
                    )
                )

        max_frontier = max(
            max_frontier,
            len(frontier)
        )

    return (
        None,
        expansions,
        max_frontier
    )


#Adaptadores para usar la misma función de A* en los dos dominios
def puzzle_h_zero(problem, state):
    return h_zero(state)


def puzzle_h_misplaced(problem, state):
    return h_misplaced(state)


def puzzle_h_manhattan(problem, state):
    return h_manhattan(state)


def puzzle_h_manhattan_x3(problem, state):
    return h_manhattan_x3(state)


def grid_h_manhattan_x3(problem, state):
    return 3 * grid_h_manhattan_scaled(
        problem,
        state
    )


def solve_one(
    domain,
    instance,
    algorithm,
    heuristic_name
):

    if domain == "8puzzle":
        problem = EightPuzzle(
            tuple(instance)
        )

    elif domain == "grid":
        problem = GridProblem(instance)

    else:
        raise ValueError(
            f"Dominio desconocido: {domain}"
        )

    start_time = time.perf_counter()

    if algorithm == "BFS":

        node, expansions, max_frontier = search_with_metrics(
            problem,
            "fifo"
        )

    elif algorithm == "DFS":

        node, expansions, max_frontier = search_with_metrics(
            problem,
            "lifo"
        )

    elif algorithm == "UCS":

        node, expansions, max_frontier = search_with_metrics(
            problem,
            "priority"
        )

    elif algorithm == "IDS":

        node, expansions, max_frontier = ids_with_metrics(
            problem
        )

    elif algorithm == "A*":

        if domain == "8puzzle":

            puzzle_heuristics = {
                "zero": puzzle_h_zero,
                "misplaced": puzzle_h_misplaced,
                "manhattan": puzzle_h_manhattan,
                "manhattan_x3": puzzle_h_manhattan_x3,
            }

            heuristic = puzzle_heuristics[
                heuristic_name
            ]

        else:

            grid_heuristics = {
                "zero": grid_h_zero,
                "manhattan_scaled": grid_h_manhattan_scaled,
                "euclidean_scaled": grid_h_euclidean_scaled,
                "manhattan_x3": grid_h_manhattan_x3,
            }

            heuristic = grid_heuristics[
                heuristic_name
            ]

        node, expansions, max_frontier = astar_with_metrics(
            problem,
            heuristic
        )

    else:
        raise ValueError(
            f"Algoritmo desconocido: {algorithm}"
        )

    wall_time = time.perf_counter() - start_time

    if node is None:
        return {
            "status": "no_solution",
            "solution_cost": None,
            "solution_length": None,
            "expansions": expansions,
            "max_frontier": max_frontier,
            "wall_time_sec": wall_time,
        }

    return {
        "status": "solved",
        "solution_cost": node.g,
        "solution_length": len(node.path()),
        "expansions": expansions,
        "max_frontier": max_frontier,
        "wall_time_sec": wall_time,
    }


#Cada prueba corre aparte para poder detenerla al llegar al timeout
def worker(
    queue,
    domain,
    instance,
    algorithm,
    heuristic_name
):

    try:

        result = solve_one(
            domain,
            instance,
            algorithm,
            heuristic_name
        )

        queue.put({
            "ok": True,
            "result": result
        })

    except Exception as error:

        queue.put({
            "ok": False,
            "error": str(error)
        })


def run_with_timeout(
    domain,
    instance,
    algorithm,
    heuristic_name,
    timeout_seconds
):

    queue = multiprocessing.Queue()

    process = multiprocessing.Process(
        target=worker,
        args=(
            queue,
            domain,
            instance,
            algorithm,
            heuristic_name
        )
    )

    process.start()
    process.join(timeout_seconds)

    if process.is_alive():

        process.terminate()
        process.join()

        return {
            "status": "timeout",
            "solution_cost": None,
            "solution_length": None,
            "expansions": None,
            "max_frontier": None,
            "wall_time_sec": timeout_seconds,
        }

    if queue.empty():

        return {
            "status": "error",
            "solution_cost": None,
            "solution_length": None,
            "expansions": None,
            "max_frontier": None,
            "wall_time_sec": None,
        }

    message = queue.get()

    if not message["ok"]:

        return {
            "status": "error",
            "solution_cost": None,
            "solution_length": None,
            "expansions": None,
            "max_frontier": None,
            "wall_time_sec": None,
        }

    return message["result"]


CSV_COLUMNS = [
    "domain",
    "level",
    "instance_id",
    "algorithm",
    "heuristic",
    "status",
    "solution_cost",
    "solution_length",
    "expansions",
    "max_frontier",
    "wall_time_sec",
    "timeout_sec",
    "instance_data",
]


def save_row(writer, row):
    writer.writerow(row)


def run_benchmark(timeout_seconds):

    puzzle_bank = load_puzzle_instances()
    grid_bank = load_grid_instances()

    RESULTS_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    puzzle_algorithms = [
        ("BFS", ""),
        ("DFS", ""),
        ("UCS", ""),
        ("IDS", ""),
        ("A*", "zero"),
        ("A*", "misplaced"),
        ("A*", "manhattan"),
        ("A*", "manhattan_x3"),
    ]

    grid_algorithms = [
        ("BFS", ""),
        ("DFS", ""),
        ("UCS", ""),
        ("IDS", ""),
        ("A*", "zero"),
        ("A*", "manhattan_scaled"),
        ("A*", "euclidean_scaled"),
        ("A*", "manhattan_x3"),
    ]

    with open(
        RESULTS_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as csv_file:

        writer = csv.DictWriter(
            csv_file,
            fieldnames=CSV_COLUMNS
        )

        writer.writeheader()

        for depth in sorted(puzzle_bank):

            states = puzzle_bank[depth]

            for index, state in enumerate(
                states,
                start=1
            ):

                for algorithm, heuristic in puzzle_algorithms:

                    print(
                        f"[8-puzzle] "
                        f"depth={depth} "
                        f"instancia={index} "
                        f"{algorithm} "
                        f"{heuristic}"
                    )

                    result = run_with_timeout(
                        domain="8puzzle",
                        instance=state,
                        algorithm=algorithm,
                        heuristic_name=heuristic,
                        timeout_seconds=timeout_seconds
                    )

                    row = {
                        "domain": "8puzzle",
                        "level": depth,
                        "instance_id": index,
                        "algorithm": algorithm,
                        "heuristic": heuristic,
                        "status": result["status"],
                        "solution_cost": result["solution_cost"],
                        "solution_length": result["solution_length"],
                        "expansions": result["expansions"],
                        "max_frontier": result["max_frontier"],
                        "wall_time_sec": result["wall_time_sec"],
                        "timeout_sec": timeout_seconds,
                        "instance_data": json.dumps(state),
                    }

                    save_row(writer, row)

                    #Se escribe cada resultado enseguida por si una corrida larga se interrumpe
                    csv_file.flush()

        for size in sorted(grid_bank):

            grids = grid_bank[size]

            for index, grid in enumerate(
                grids,
                start=1
            ):

                for algorithm, heuristic in grid_algorithms:

                    print(
                        f"[grid] "
                        f"size={size}x{size} "
                        f"instancia={index} "
                        f"{algorithm} "
                        f"{heuristic}"
                    )

                    result = run_with_timeout(
                        domain="grid",
                        instance=grid,
                        algorithm=algorithm,
                        heuristic_name=heuristic,
                        timeout_seconds=timeout_seconds
                    )

                    row = {
                        "domain": "grid",
                        "level": size,
                        "instance_id": index,
                        "algorithm": algorithm,
                        "heuristic": heuristic,
                        "status": result["status"],
                        "solution_cost": result["solution_cost"],
                        "solution_length": result["solution_length"],
                        "expansions": result["expansions"],
                        "max_frontier": result["max_frontier"],
                        "wall_time_sec": result["wall_time_sec"],
                        "timeout_sec": timeout_seconds,
                        "instance_data": json.dumps(grid),
                    }

                    save_row(writer, row)
                    csv_file.flush()

    print()
    print("Benchmark terminado.")
    print("Resultados guardados en:")
    print(RESULTS_FILE)


def main():

    parser = argparse.ArgumentParser(
        description="Benchmark de la Parte 1 del HW1"
    )

    parser.add_argument(
        "--timeout",
        type=float,
        required=True,
        help="Timeout en segundos para cada ejecución"
    )

    args = parser.parse_args()

    if args.timeout <= 0:
        raise ValueError(
            "El timeout debe ser mayor que 0."
        )

    run_benchmark(args.timeout)


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()