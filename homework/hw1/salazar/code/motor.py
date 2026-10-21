"""Motor de búsqueda instrumentado del grupo (base compartida, responsable: Daniel).

Reproduce el ``search()`` del curso (``curso/week03/search.py``) con la misma
disciplina de frontera y los mismos dos detalles que pide el profe:

  1. el test de meta se hace al EXPANDIR, no al generar;
  2. ``expansions`` cuenta nodos expandidos (estados sacados de la frontera y no
     explorados antes), exactamente como el original.

Lo que agregamos, porque el Duel 1 lo exige y el original no lo mide:

  * tamaño máximo de la frontera;
  * tiempo de reloj (``time.perf_counter``);
  * un timeout duro: al pasar el límite devolvemos ``status="timeout"``. Un timeout
    NO es "no hay solución" y se reporta aparte;
  * A* como una disciplina más de la misma frontera (prioridad ``g + h``).

``test_group.py`` comprueba que nuestras expansiones son idénticas a las del
``search()`` del curso en BFS, DFS y UCS. Si alguien cambia este archivo, esa
prueba es la que avisa.

Uso:
    from motor import resolver
    r = resolver(problema, "astar", h=h_manhattan, timeout_s=30)
    r.status, r.cost, r.length, r.expansions, r.max_frontier, r.seconds, r.path
"""
from __future__ import annotations

import heapq
import itertools
import time
from collections import deque
from dataclasses import dataclass, field

# Nodo y fixtures del curso, sin copiarlos: la interfaz es la misma.
from rutas import preparar_rutas

preparar_rutas()
from search import Node  # noqa: E402  (curso/week03/search.py, intacto)

TIMEOUT_S = 30.0          # timeout duro por corrida (algoritmo × instancia)
CHEQUEO_RELOJ = 256       # revisamos el reloj cada N expansiones


class Timeout(Exception):
    """Se lanza dentro del bucle cuando se acaba el tiempo."""


@dataclass
class Resultado:
    status: str                    # "solved" | "timeout" | "no_solution"
    cost: float | None             # costo g del camino (None si no resolvió)
    length: int | None             # número de acciones
    expansions: int                # nodos expandidos (hasta el corte, si hubo timeout)
    max_frontier: int              # máximo de nodos en la frontera
    seconds: float                 # tiempo de reloj
    path: list = field(default_factory=list)

    def fila(self) -> dict:
        """Columnas que van al CSV (sin el camino completo)."""
        return {"status": self.status, "cost": self.cost, "length": self.length,
                "expansions": self.expansions, "max_frontier": self.max_frontier,
                "seconds": round(self.seconds, 6)}


class _Frontera:
    """FIFO -> BFS, LIFO -> DFS, prioridad g -> UCS, prioridad g+h -> A*."""

    def __init__(self, tipo, h=None, problema=None):
        self.tipo, self.h, self.problema = tipo, h, problema
        self.contador = itertools.count()      # desempate estable, como el curso
        self.datos = deque() if tipo in ("fifo", "lifo") else []

    def push(self, nodo):
        if self.tipo == "priority":
            heapq.heappush(self.datos, (nodo.g, next(self.contador), nodo))
        elif self.tipo == "astar":
            f = nodo.g + self.h(self.problema, nodo.state)
            heapq.heappush(self.datos, (f, next(self.contador), nodo))
        else:
            self.datos.append(nodo)

    def pop(self):
        if self.tipo in ("priority", "astar"):
            return heapq.heappop(self.datos)[2]
        return self.datos.popleft() if self.tipo == "fifo" else self.datos.pop()

    def __len__(self):
        return len(self.datos)


def _busqueda_grafo(problema, tipo, h, limite):
    """Mismo bucle que ``search()`` del curso, con frontera máxima y reloj."""
    inicio = Node(problema.initial)
    if problema.is_goal(inicio.state):
        return inicio, 0, 1
    frontera = _Frontera(tipo, h, problema)
    frontera.push(inicio)
    explorados = set()
    expansiones, max_frontera = 0, 1
    while frontera:
        nodo = frontera.pop()
        if problema.is_goal(nodo.state):       # test de meta al expandir
            return nodo, expansiones, max_frontera
        if nodo.state in explorados:
            continue
        explorados.add(nodo.state)
        expansiones += 1
        if expansiones % CHEQUEO_RELOJ == 0 and time.perf_counter() > limite:
            raise Timeout(expansiones, max_frontera)
        for accion in problema.actions(nodo.state):
            hijo = problema.result(nodo.state, accion)
            if hijo not in explorados:
                costo = problema.step_cost(nodo.state, accion)
                frontera.push(Node(hijo, nodo, accion, nodo.g + costo))
        max_frontera = max(max_frontera, len(frontera))
    return None, expansiones, max_frontera


def _ids(problema, limite, max_depth=60):
    """IDS de nuestra hw3 (conjunto del camino actual contra ciclos).

    "Frontera" en IDS: no hay cola; medimos el máximo de nodos guardados a la vez,
    es decir la profundidad máxima de la pila de recursión (el O(bd) de la teoría
    se refiere a los hermanos pendientes; documentado en DECISION_NOTES.md).
    """
    total, max_pila = 0, 1

    def limitado(tope):
        nonlocal total, max_pila
        en_camino = {problema.initial}

        def visitar(nodo, restante, prof):
            nonlocal total, max_pila
            max_pila = max(max_pila, prof + 1)
            if problema.is_goal(nodo.state):
                return nodo, False
            if restante == 0:
                puede = any(problema.result(nodo.state, a) not in en_camino
                            for a in problema.actions(nodo.state))
                return None, puede
            total += 1
            if total % CHEQUEO_RELOJ == 0 and time.perf_counter() > limite:
                raise Timeout(total, max_pila)
            corte = False
            for accion in problema.actions(nodo.state):
                estado = problema.result(nodo.state, accion)
                if estado in en_camino:
                    continue
                hijo = Node(estado, nodo, accion,
                            nodo.g + problema.step_cost(nodo.state, accion))
                en_camino.add(estado)
                hallado, c = visitar(hijo, restante - 1, prof + 1)
                en_camino.remove(estado)
                if hallado is not None:
                    return hallado, False
                corte = corte or c
            return None, corte

        return visitar(Node(problema.initial), tope, 0)

    for tope in range(max_depth + 1):
        nodo, corte = limitado(tope)
        if nodo is not None or not corte:
            return nodo, total, max_pila
    return None, total, max_pila


ALGORITMOS = ("bfs", "dfs", "ucs", "ids", "astar")
_TIPO = {"bfs": "fifo", "dfs": "lifo", "ucs": "priority", "astar": "astar"}


def resolver(problema, algoritmo, h=None, timeout_s=TIMEOUT_S) -> Resultado:
    """Corre un algoritmo sobre un problema con timeout duro y métricas."""
    if algoritmo not in ALGORITMOS:
        raise ValueError(f"algoritmo desconocido: {algoritmo!r}")
    if algoritmo == "astar" and h is None:
        raise ValueError("A* necesita una heurística h(problema, estado)")
    t0 = time.perf_counter()
    limite = t0 + timeout_s
    try:
        if algoritmo == "ids":
            nodo, exp, maxf = _ids(problema, limite)
        else:
            nodo, exp, maxf = _busqueda_grafo(problema, _TIPO[algoritmo], h, limite)
    except Timeout as corte:
        exp, maxf = corte.args
        return Resultado("timeout", None, None, exp, maxf, time.perf_counter() - t0)
    seg = time.perf_counter() - t0
    if nodo is None:
        return Resultado("no_solution", None, None, exp, maxf, seg)
    camino = nodo.path()
    return Resultado("solved", nodo.g, len(camino), exp, maxf, seg, camino)
