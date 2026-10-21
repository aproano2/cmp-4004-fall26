"""Garantía de las heurísticas del 8-puzzle en TODOS los estados (eje 2).

Las pruebas de aceptación revisan las 40 instancias del banco. Aquí lo
comprobamos en los 181 440 estados alcanzables: un BFS hacia atrás desde la
meta da la distancia real h*(s) de cada estado (todo movimiento cuesta 1), y
contamos cuántas veces cada heurística la sobreestima o deja de dominar.

Comprobamos:
  admisible   h(s) <= h*(s)
  consistente h(s) <= 1 + h(s') para cada vecino s'
  dominancia  manhattan(s) >= misplaced(s)

Uso:  python code/admisibilidad_exhaustiva.py
Salida: results/admisibilidad_exhaustiva.csv
"""
from collections import deque

from rutas import RESULTS, preparar_rutas

preparar_rutas()
import heuristicas as H  # noqa: E402
from estadistica import escribir_csv  # noqa: E402
from search import GOAL, EightPuzzle  # noqa: E402


def distancias_reales():
    """{estado: h*} para todos los estados alcanzables desde la meta."""
    prob = EightPuzzle(GOAL)
    dist = {GOAL: 0}
    cola = deque([GOAL])
    while cola:
        s = cola.popleft()
        for a in prob.actions(s):
            t = prob.result(s, a)
            if t not in dist:
                dist[t] = dist[s] + 1
                cola.append(t)
    return dist, prob


def comprobar():
    dist, prob = distancias_reales()
    hs = {"misplaced": H.h_misplaced, "manhattan": H.h_manhattan_puzzle}
    filas = []
    for nombre, h in hs.items():
        sobre = incons = 0
        maxh = 0
        for s, d in dist.items():
            v = h(prob, s)
            maxh = max(maxh, v)
            sobre += v > d
            incons += any(v > 1 + h(prob, prob.result(s, a)) for a in prob.actions(s))
        filas.append({"heuristica": nombre, "estados": len(dist),
                      "sobreestima": sobre, "inconsistente": incons, "h_max": maxh,
                      "h_star_max": max(dist.values())})
    no_domina = sum(H.h_manhattan_puzzle(prob, s) < H.h_misplaced(prob, s) for s in dist)
    for f in filas:
        f["manhattan_no_domina"] = no_domina
    return filas


if __name__ == "__main__":
    filas = comprobar()
    escribir_csv(RESULTS / "admisibilidad_exhaustiva.csv", filas)
    for f in filas:
        print(f)
