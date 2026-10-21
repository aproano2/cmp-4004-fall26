"""Heurísticas del Duel 1. Autoría: Andretty Ochoa.

Firma obligatoria de toda heurística:  h(problema, estado) -> número >= 0
(la misma que usa ``gridworld.astar`` del curso y nuestro ``motor.resolver``).

Mientras una función lance NotImplementedError, ``benchmark.py`` se salta las
configuraciones de A* que la usan y lo avisa; el resto del grupo puede trabajar.
Cuando termines, ``python code/tests/test_heuristicas.py`` debe pasar completo.
"""
from rutas import preparar_rutas

preparar_rutas()
from gridworld import MIN_COST          # noqa: E402  = 1 en el banco del curso
from search import GOAL                 # noqa: E402  (1,2,3,4,5,6,7,8,0)


def h_cero(problema, estado):
    """h = 0. A* con h_cero es UCS. Ya está hecha: sirve de control."""
    return 0


# ---- 8-puzzle -----------------------------------------------------------------

def h_misplaced(problema, estado):
    """Número de fichas fuera de su lugar. NO cuenta el blanco (0).

    Si cuentas el blanco deja de ser admisible: un estado a 1 movimiento de la
    meta daría 2. Ejemplo: (1,2,3,4,5,6,7,0,8) -> 1.
    """
    goal = getattr(problema, "goal", GOAL)

    return sum(
        1
        for actual, esperado in zip(estado, goal)
        if actual != 0 and actual != esperado
    )


def h_manhattan_puzzle(problema, estado):
    """Suma, sobre las fichas 1..8, de |fila - fila_meta| + |col - col_meta|.

    Tampoco cuenta el blanco. Usa ``problema.goal`` (o GOAL) para ubicar cada ficha;
    no asumas que la ficha k va en la posición k-1. Ejemplo:
    (1,2,3,4,5,6,7,0,8) -> 1.
    """
    goal = getattr(problema, "goal", GOAL)

    pos_goal = {
        ficha: divmod(i, 3)
        for i, ficha in enumerate(goal)
    }

    distancia = 0

    for i, ficha in enumerate(estado):
        if ficha == 0:
            continue

        fila, columna = divmod(i, 3)
        fila_goal, columna_goal = pos_goal[ficha]

        distancia += abs(fila - fila_goal) + abs(columna - columna_goal)

    return distancia


# ---- grilla con terrenos ---------------------------------------------------------

def h_manhattan_grid(problema, estado):
    """Manhattan × MIN_COST hasta ``problema.goal``.

    Admisible porque cada paso cuesta al menos MIN_COST. Explica en
    DECISION_NOTES.md por qué la Manhattan sin escalar dejaría de serlo si
    MIN_COST fuera menor que 1 (por ejemplo 0.5).
    """
    fila, columna = estado
    fila_goal, columna_goal = problema.goal

    distancia = abs(fila - fila_goal) + abs(columna - columna_goal)

    return distancia * MIN_COST


# ---- admisibilidad rota a propósito (análisis 3) ------------------------------------

def inflar(h, factor=3):
    """Devuelve una heurística nueva: estado -> factor * h(problema, estado).

    Debe conservar un nombre legible (``h_x.__name__ = f"{h.__name__}_x{factor}"``)
    para que aparezca bien en los CSV.
    """
    def h_inflada(problema, estado):
        return factor * h(problema, estado)

    h_inflada.__name__ = f"{h.__name__}_x{factor}"

    return h_inflada


def registro():
    """Heurísticas que corre benchmark.py: {dominio: {nombre: función}}.

    No cambies los nombres: son la columna ``heuristic`` de los CSV y los usan
    los análisis y las figuras de todo el grupo.
    """
    out = {"8puzzle": {"misplaced": h_misplaced,
                       "manhattan": h_manhattan_puzzle},
           "grid": {"manhattan": h_manhattan_grid}}
    for dominio in out:
        try:
            out[dominio]["manhattan_x3"] = inflar(out[dominio]["manhattan"], 3)
        except NotImplementedError:
            pass
    return out
