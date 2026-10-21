"""Algoritmos de búsqueda para el Duelo 1: BFS, DFS, UCS, IDS y A*.

Se usa la misma interfaz Problem de los studios de las semanas 3 y 4:

    problem.initial
    problem.actions(state)        -> acciones legales
    problem.result(state, action) -> estado siguiente
    problem.is_goal(state)        -> bool
    problem.step_cost(s, action)  -> costo de aplicar `action` en `s`

Lo nuevo respecto al código del studio es la instrumentación. Cada algoritmo
devuelve un ``Result`` con las cuatro cosas que pide el deber (costo y longitud,
expansiones, tamaño máximo de la frontera, tiempo de reloj) y respeta un timeout
duro. Una corrida que llega al timeout se reporta con status "timeout", nunca
como "sin solución".

Dos detalles que importan para la corrección (ambos de la semana 3):
  * el test de meta se hace al EXPANDIR el nodo, no al generarlo;
  * A* reabre un estado cuando encuentra un camino más barato hacia él, así
    sigue siendo correcto con una heurística inconsistente (necesario para el
    experimento de h x 3).
"""
from collections import deque
from dataclasses import dataclass
import heapq
import itertools
import time

TIMEOUT_S = 10.0          # timeout duro por corrida (algoritmo, instancia)
_CHECK_EVERY = 512        # cada cuántas expansiones se revisa el reloj


class Node:
    __slots__ = ("state", "parent", "action", "g", "depth")

    def __init__(self, state, parent=None, action=None, g=0):
        self.state, self.parent, self.action, self.g = state, parent, action, g
        self.depth = 0 if parent is None else parent.depth + 1

    def path(self):
        node, out = self, []
        while node.parent is not None:
            out.append(node.action)
            node = node.parent
        return out[::-1]


@dataclass
class Result:
    algorithm: str
    status: str                # "solved" | "timeout" | "exhausted"
    cost: float = None         # suma de los costos de paso del camino devuelto
    length: int = None         # número de acciones del camino devuelto
    expansions: int = 0        # nodos cuyos sucesores se generaron
    generated: int = 0         # nodos creados (se usa para b*)
    max_frontier: int = 0      # máximo de nodos esperando en la frontera
    time_s: float = 0.0
    path: list = None

    @property
    def solved(self):
        return self.status == "solved"


def _finish(name, status, node, expansions, generated, max_frontier, t0):
    res = Result(name, status, expansions=expansions, generated=generated,
                 max_frontier=max_frontier, time_s=time.perf_counter() - t0)
    if node is not None:
        res.path = node.path()
        res.cost, res.length = node.g, len(res.path)
    return res


# ---------------------------------------------------------------------------
# BFS / DFS / UCS: un solo ciclo, tres disciplinas de frontera
# ---------------------------------------------------------------------------

class Frontier:
    """fifo -> BFS, lifo -> DFS, priority (por g) -> UCS."""

    def __init__(self, kind):
        self.kind = kind
        self.counter = itertools.count()
        self.data = [] if kind == "priority" else deque()

    def push(self, node):
        if self.kind == "priority":
            heapq.heappush(self.data, (node.g, next(self.counter), node))
        else:
            self.data.append(node)

    def pop(self):
        if self.kind == "priority":
            return heapq.heappop(self.data)[2]
        if self.kind == "fifo":
            return self.data.popleft()
        return self.data.pop()

    def __len__(self):
        return len(self.data)


def graph_search(problem, kind, name, timeout=TIMEOUT_S):
    """Búsqueda en grafo genérica con conjunto de explorados."""
    t0 = time.perf_counter()
    frontier = Frontier(kind)
    frontier.push(Node(problem.initial))
    explored = set()
    expansions, generated, max_frontier = 0, 1, 1

    while frontier:
        node = frontier.pop()
        if problem.is_goal(node.state):              # test de meta al expandir
            return _finish(name, "solved", node, expansions, generated,
                           max_frontier, t0)
        if node.state in explored:
            continue
        explored.add(node.state)
        expansions += 1
        if expansions % _CHECK_EVERY == 0 and time.perf_counter() - t0 > timeout:
            return _finish(name, "timeout", None, expansions, generated,
                           max_frontier, t0)
        for action in problem.actions(node.state):
            child = problem.result(node.state, action)
            if child not in explored:
                frontier.push(Node(child, node, action,
                                   node.g + problem.step_cost(node.state, action)))
                generated += 1
        if len(frontier) > max_frontier:
            max_frontier = len(frontier)
    return _finish(name, "exhausted", None, expansions, generated, max_frontier, t0)


def bfs(problem, timeout=TIMEOUT_S):
    """Completo. Óptimo SOLO cuando todos los pasos cuestan lo mismo."""
    return graph_search(problem, "fifo", "BFS", timeout)


def dfs(problem, timeout=TIMEOUT_S):
    """Termina en espacios finitos gracias al conjunto de explorados. No es óptimo."""
    return graph_search(problem, "lifo", "DFS", timeout)


def ucs(problem, timeout=TIMEOUT_S):
    """Óptimo para cualquier costo de paso no negativo."""
    return graph_search(problem, "priority", "UCS", timeout)


# ---------------------------------------------------------------------------
# IDS: DFS con límite de profundidad (búsqueda en árbol), iterado
# ---------------------------------------------------------------------------

def _on_path(node, state):
    """True si `state` ya aparece entre `node` y la raíz."""
    while node is not None:
        if node.state == state:
            return True
        node = node.parent
    return False


def ids(problem, timeout=TIMEOUT_S, max_depth=80):
    """Profundización iterativa. Sin conjunto de explorados: la memoria es
    O(b*d) y el precio es re-expandir estados. El único control de ciclos es
    "no volver a un estado que ya está en el camino actual". Igual que BFS,
    devuelve una solución de mínima profundidad, así que es óptimo solo con
    costos uniformes.

    Usa una pila explícita (en vez de recursión) para poder medir la frontera:
    es el tamaño máximo de esa pila.
    """
    t0 = time.perf_counter()
    expansions, generated, max_frontier = 0, 0, 1

    for limit in range(max_depth + 1):
        stack = [Node(problem.initial)]
        generated += 1
        cutoff = False
        while stack:
            node = stack.pop()
            if problem.is_goal(node.state):
                return _finish("IDS", "solved", node, expansions, generated,
                               max_frontier, t0)
            if node.depth == limit:
                cutoff = True
                continue
            expansions += 1
            if expansions % _CHECK_EVERY == 0 and time.perf_counter() - t0 > timeout:
                return _finish("IDS", "timeout", None, expansions, generated,
                               max_frontier, t0)
            for action in problem.actions(node.state):
                child = problem.result(node.state, action)
                if not _on_path(node, child):
                    stack.append(Node(child, node, action,
                                      node.g + problem.step_cost(node.state, action)))
                    generated += 1
            if len(stack) > max_frontier:
                max_frontier = len(stack)
        if not cutoff:                               # no queda nada bajo el límite
            return _finish("IDS", "exhausted", None, expansions, generated,
                           max_frontier, t0)
    return _finish("IDS", "exhausted", None, expansions, generated, max_frontier, t0)


# ---------------------------------------------------------------------------
# A*
# ---------------------------------------------------------------------------

def astar(problem, h, weight=1.0, name="A*", timeout=TIMEOUT_S):
    """A* con f = g + weight * h.

    weight = 1 y h admisible  ->  el camino devuelto es óptimo.
    weight > 1 rompe la admisibilidad a propósito (Parte 1, análisis 3).

    Los empates en f se rompen hacia la h más pequeña (el nodo más cercano a la
    meta). ``max_frontier`` cuenta las entradas del heap, incluidas las obsoletas.
    """
    t0 = time.perf_counter()
    counter = itertools.count()
    start = Node(problem.initial)
    h0 = weight * h(problem, start.state)
    frontier = [(h0, h0, next(counter), start)]
    best_g = {problem.initial: 0}
    expansions, generated, max_frontier = 0, 1, 1

    while frontier:
        _, _, _, node = heapq.heappop(frontier)
        if node.g > best_g[node.state]:
            continue                                 # entrada obsoleta
        if problem.is_goal(node.state):              # test de meta al expandir
            return _finish(name, "solved", node, expansions, generated,
                           max_frontier, t0)
        expansions += 1
        if expansions % _CHECK_EVERY == 0 and time.perf_counter() - t0 > timeout:
            return _finish(name, "timeout", None, expansions, generated,
                           max_frontier, t0)
        for action in problem.actions(node.state):
            child = problem.result(node.state, action)
            g2 = node.g + problem.step_cost(node.state, action)
            if g2 < best_g.get(child, float("inf")):
                best_g[child] = g2
                hc = weight * h(problem, child)
                heapq.heappush(frontier,
                               (g2 + hc, hc, next(counter), Node(child, node, action, g2)))
                generated += 1
        if len(frontier) > max_frontier:
            max_frontier = len(frontier)
    return _finish(name, "exhausted", None, expansions, generated, max_frontier, t0)


# ---------------------------------------------------------------------------
# Factor de ramificación efectivo
# ---------------------------------------------------------------------------

def effective_branching_factor(n_nodes, depth, tol=1e-6):
    """b* tal que un árbol uniforme de profundidad `depth` tiene n_nodes + 1 nodos:

        N + 1 = 1 + b* + b*^2 + ... + b*^d          (R&N sección 3.6.1)

    N es el número de nodos generados por la búsqueda. Se resuelve por bisección.
    """
    if depth <= 0 or n_nodes <= 0:
        return float("nan")
    if n_nodes <= depth:
        return 1.0

    def total(b):
        return sum(b ** i for i in range(depth + 1))

    lo, hi = 1.0, float(n_nodes)
    while hi - lo > tol:
        mid = (lo + hi) / 2
        if total(mid) < n_nodes + 1:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2
