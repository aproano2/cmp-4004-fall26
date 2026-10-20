from gridworld import GridProblem, render
from search import bfs, ucs, astar


def grid_manhattan(problem, state):
    r, c = state
    gr, gc = problem.goal

    return abs(r - gr) + abs(c - gc)


grid = [
    "S~G",
    "...",
]

problem = GridProblem(grid)

print("GRID")
print(render(grid))
print()

algorithms = [
    ("BFS", lambda: bfs(problem)),
    ("UCS", lambda: ucs(problem)),
    (
        "A* Manhattan",
        lambda: astar(
            problem,
            lambda state: grid_manhattan(problem, state)
        )
    ),
]

for name, algorithm in algorithms:

    node, expansions, max_frontier = algorithm()

    print(name)
    print("Path:", node.path())
    print("Cost:", node.g)
    print("Length:", len(node.path()))
    print("Expansions:", expansions)
    print("Max frontier:", max_frontier)
    print()