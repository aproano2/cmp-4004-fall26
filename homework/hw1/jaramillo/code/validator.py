"""Validador de las respuestas del modelo. Al modelo nunca se le pregunta si
acertó: cada respuesta se vuelve a ejecutar aquí, movimiento por movimiento,
contra la instancia real.

Categorías (las tres categorías de falla del deber más dos, para que nada quede
escondido dentro de otra):

    correct      camino legal, óptimo, y el costo reportado es el correcto
    wrong_cost   camino legal y óptimo, pero el costo reportado está mal
    suboptimal   camino legal que llega a la meta, pero cuesta más que el de A*
    illegal      se sale del tablero, entra a una pared, usa un movimiento
                 desconocido o no termina en la meta
    no_answer    no se pudo leer una línea PATH (respuesta mal formada o
                 timeout del modelo)
"""
import re
from dataclasses import dataclass

from domains import MOVES, TERRAIN, WALL, GridProblem, EightPuzzle, GOAL

CATEGORIES = ["correct", "wrong_cost", "suboptimal", "illegal", "no_answer"]


@dataclass
class Verdict:
    category: str
    detail: str
    path: str = None
    reported_cost: int = None
    true_cost: int = None        # recalculado recorriendo el camino (None si es ilegal)
    optimal_cost: int = None

    @property
    def optimal_path(self):
        """Camino legal de costo óptimo, diga lo que diga el modelo sobre el costo."""
        return self.category in ("correct", "wrong_cost")


def parse_reply(text):
    """Extrae las ÚLTIMAS líneas 'PATH:' y 'COST:' de una respuesta (el modelo
    puede razonar en voz alta antes). Es tolerante a propósito: acepta
    minúsculas, asteriscos de markdown y separadores como espacios, comas o
    flechas entre movimientos. Devuelve (camino o None, costo o None)."""
    path, cost = None, None
    for line in (text or "").splitlines():
        clean = line.replace("*", "").replace("`", "").strip()
        m = re.match(r"(?i)^PATH\s*[:=]\s*(.*)$", clean)
        if m:
            letters = re.sub(r"[\s,;\-\>→\[\]\(\)\.'\"]", "", m.group(1)).upper()
            path = letters
        m = re.match(r"(?i)^(?:TOTAL\s+)?COST\s*[:=]\s*(-?\d+)", clean)
        if m:
            cost = int(m.group(1))
    return path, cost


def walk_grid(grid, path):
    """Recorre `path` sobre el grid. Devuelve (costo_real, None) si es legal y
    termina en G; si no, (None, motivo)."""
    prob = GridProblem(grid)
    (r, c), total = prob.initial, 0
    for k, ch in enumerate(path, 1):
        if ch not in MOVES:
            return None, f"movimiento {k}: símbolo desconocido {ch!r}"
        dr, dc = MOVES[ch]
        r, c = r + dr, c + dc
        if not (0 <= r < prob.rows and 0 <= c < prob.cols):
            return None, f"el movimiento {k} ({ch}) se sale del grid"
        if prob.grid[r][c] == WALL:
            return None, f"el movimiento {k} ({ch}) entra a una pared"
        total += TERRAIN[prob.grid[r][c]]
    if (r, c) != prob.goal:
        return None, f"el camino termina en {(r, c)}, la meta es {prob.goal}"
    return total, None


def walk_puzzle(state, path):
    """Lo mismo para el 8-puzzle: cada letra mueve el hueco. Costo = movimientos."""
    prob = EightPuzzle(state)
    s = prob.initial
    for k, ch in enumerate(path, 1):
        if ch not in MOVES:
            return None, f"movimiento {k}: símbolo desconocido {ch!r}"
        if ch not in prob.actions(s):
            return None, f"el movimiento {k} ({ch}) saca el hueco del tablero"
        s = prob.result(s, ch)
    if s != GOAL:
        return None, "el tablero final no es la meta"
    return len(path), None


def validate(domain, instance, path, reported_cost, optimal_cost):
    """Clasifica una respuesta. `optimal_cost` viene de A* con h admisible."""
    if path is None:
        return Verdict("no_answer", "no se encontró una línea PATH", None,
                       reported_cost, None, optimal_cost)
    walk = walk_grid if domain == "grid" else walk_puzzle
    true_cost, why = walk(instance, path)
    if true_cost is None:
        return Verdict("illegal", why, path, reported_cost, None, optimal_cost)
    assert true_cost >= optimal_cost, "camino legal más barato que A*: bug en A*"
    if true_cost > optimal_cost:
        return Verdict("suboptimal", f"costo {true_cost} > óptimo {optimal_cost}",
                       path, reported_cost, true_cost, optimal_cost)
    if reported_cost != true_cost:
        return Verdict("wrong_cost", f"reportó {reported_cost}, real {true_cost}",
                       path, reported_cost, true_cost, optimal_cost)
    return Verdict("correct", "", path, reported_cost, true_cost, optimal_cost)
