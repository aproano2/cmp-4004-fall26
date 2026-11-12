"""Los dos dominios del Duelo 1 y sus heurísticas.

* 8-puzzle: costo uniforme (cada movimiento cuesta 1).
* Grid con pesos: el costo de un movimiento es el terreno de la celda a la que
  se ENTRA.

En los dos dominios una acción es una de las letras U / D / L / R (arriba,
abajo, izquierda, derecha). En el 8-puzzle la letra dice hacia dónde se mueve
el HUECO. Usar el mismo alfabeto en ambos dominios permite que los algoritmos
clásicos, el LLM y el validador hablen el mismo idioma.

Los bancos de instancias son los de los studios (semilla 20260807):
    instances/puzzle.json  10 puzzles por cada profundidad óptima 4, 8, 12, 16
    instances/grid.json    10 grids por cada tamaño 5x5, 8x8, 12x12, 16x16
"""
import json
from pathlib import Path

HERE = Path(__file__).parent
MOVES = {"U": (-1, 0), "D": (1, 0), "L": (0, -1), "R": (0, 1)}

# ---------------------------------------------------------------------------
# 8-puzzle
# ---------------------------------------------------------------------------

GOAL = (1, 2, 3, 4, 5, 6, 7, 8, 0)


class EightPuzzle:
    """Estado: tupla de 9 leída fila por fila; 0 es el hueco."""

    def __init__(self, initial, goal=GOAL):
        self.initial, self.goal = tuple(initial), tuple(goal)

    def actions(self, state):
        r, c = divmod(state.index(0), 3)
        return tuple(m for m, (dr, dc) in MOVES.items()
                     if 0 <= r + dr < 3 and 0 <= c + dc < 3)

    def result(self, state, action):
        b = state.index(0)
        dr, dc = MOVES[action]
        t = b + 3 * dr + dc
        s = list(state)
        s[b], s[t] = s[t], s[b]
        return tuple(s)

    def is_goal(self, state):
        return state == self.goal

    def step_cost(self, state, action):
        return 1


def h_misplaced(problem, state):
    """Número de fichas (sin contar el hueco) que no están en su celda meta.
    Admisible: cada ficha mal ubicada necesita al menos un movimiento."""
    return sum(1 for v, g in zip(state, problem.goal) if v != 0 and v != g)


def h_manhattan_puzzle(problem, state):
    """Suma, sobre las fichas (sin el hueco), de la distancia en filas más
    columnas a su celda meta. Admisible: un movimiento desplaza una sola ficha
    una sola celda. Domina a h_misplaced, porque toda ficha mal ubicada está a
    distancia >= 1."""
    total = 0
    for i, v in enumerate(state):
        if v != 0:
            j = problem.goal.index(v)
            total += abs(i // 3 - j // 3) + abs(i % 3 - j % 3)
    return total


def is_solvable(state):
    """Un estado puede llegar a GOAL si y solo si su número de inversiones es par."""
    tiles = [v for v in state if v != 0]
    inv = sum(1 for i in range(len(tiles)) for j in range(i + 1, len(tiles))
              if tiles[i] > tiles[j])
    return inv % 2 == 0


def render_puzzle(state):
    return "\n".join(" ".join("_" if v == 0 else str(v) for v in state[r:r + 3])
                     for r in range(0, 9, 3))


# ---------------------------------------------------------------------------
# Grid con pesos
# ---------------------------------------------------------------------------

TERRAIN = {".": 1, ",": 3, "~": 8, "S": 1, "G": 1}
WALL = "#"                      # intransitable; el banco del curso no tiene
MIN_COST = min(TERRAIN.values())


class GridProblem:
    """Estado: (fila, columna). Costo de un movimiento = terreno de la celda destino."""

    def __init__(self, grid):
        self.grid = list(grid)
        self.rows, self.cols = len(grid), len(grid[0])
        self.initial = self._find("S")
        self.goal = self._find("G")

    def _find(self, ch):
        for r, row in enumerate(self.grid):
            c = row.find(ch)
            if c != -1:
                return (r, c)
        raise ValueError(f"el grid no tiene {ch!r}")

    def passable(self, r, c):
        return (0 <= r < self.rows and 0 <= c < self.cols
                and self.grid[r][c] != WALL)

    def actions(self, state):
        r, c = state
        return tuple(m for m, (dr, dc) in MOVES.items()
                     if self.passable(r + dr, c + dc))

    def result(self, state, action):
        dr, dc = MOVES[action]
        return (state[0] + dr, state[1] + dc)

    def is_goal(self, state):
        return state == self.goal

    def step_cost(self, state, action):
        r, c = self.result(state, action)
        return TERRAIN[self.grid[r][c]]


def h_zero(problem, state):
    return 0


def h_manhattan_grid(problem, state):
    """Distancia Manhattan x terreno más barato. Admisible porque cada uno de
    los |dr| + |dc| movimientos que faltan cuesta al menos MIN_COST."""
    return (abs(state[0] - problem.goal[0]) + abs(state[1] - problem.goal[1])) * MIN_COST


def render_grid(grid):
    return "\n".join(" ".join(row) for row in grid)


# ---------------------------------------------------------------------------
# Bancos de instancias
# ---------------------------------------------------------------------------

def load_puzzles(path=None):
    """{profundidad: [estado, ...]}"""
    data = json.loads(Path(path or HERE / "instances" / "puzzle.json")
                      .read_text(encoding="utf-8"))
    return {int(k): [tuple(s) for s in v] for k, v in data["instances"].items()}


def load_grids(path=None):
    """{tamaño: [grid, ...]} donde cada grid es una lista de strings."""
    data = json.loads(Path(path or HERE / "instances" / "grid.json")
                      .read_text(encoding="utf-8"))
    return {int(k): v for k, v in data["instances"].items()}


def all_instances():
    """Todas las instancias de los dos dominios: (dominio, nivel, índice, instancia)."""
    out = []
    for depth, states in sorted(load_puzzles().items()):
        out += [("puzzle", depth, i, s) for i, s in enumerate(states)]
    for size, grids in sorted(load_grids().items()):
        out += [("grid", size, i, g) for i, g in enumerate(grids)]
    return out


def make_problem(domain, instance):
    return EightPuzzle(instance) if domain == "puzzle" else GridProblem(instance)


def admissible_h(domain):
    return h_manhattan_puzzle if domain == "puzzle" else h_manhattan_grid
