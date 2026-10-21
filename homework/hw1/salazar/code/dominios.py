"""Los dos dominios del Duel 1 y sus bancos de instancias (base compartida).

Usamos los bancos del curso tal cual, con la semilla 20260807:

  * 8-puzzle: ``curso/week03/instances.json``, profundidades óptimas 4, 8, 12, 16
    (verificadas por BFS exhaustivo en el generador del profe), 10 por nivel.
  * Grilla con terrenos: ``curso/week04/instances.json``, tamaños 5, 8, 12, 16,
    10 por nivel. Costos al ENTRAR a una celda: '.'=1, ','=3, '~'=8, 'S'/'G'=1.
    Estas grillas no tienen paredes; ver DECISION_NOTES.md.

Cada instancia tiene un id estable que se usa en TODOS los CSV del grupo:
``8puzzle-12-03`` = dominio, nivel, índice 0..9. Así podemos cruzar las
mediciones clásicas, las del LLM y las del brazo con herramienta.
"""
from rutas import preparar_rutas

preparar_rutas()
import gridworld                       # noqa: E402  curso/week04, intacto
import search                          # noqa: E402  curso/week03, intacto

DOMINIOS = ("8puzzle", "grid")
NIVELES = {"8puzzle": (4, 8, 12, 16), "grid": (5, 8, 12, 16)}


def banco(dominio):
    """{nivel: [instancia, ...]}. Instancia = 9-tupla (8-puzzle) o list[str] (grilla)."""
    if dominio == "8puzzle":
        return search.load_instances()
    if dominio == "grid":
        return gridworld.load_instances()
    raise ValueError(dominio)


def instancias(dominio, niveles=None, por_nivel=None):
    """Itera (id, nivel, instancia) en orden fijo: nivel creciente, índice 0..9."""
    datos = banco(dominio)
    for nivel in niveles or NIVELES[dominio]:
        for i, inst in enumerate(datos[nivel][:por_nivel]):
            yield f"{dominio}-{nivel}-{i:02d}", nivel, inst


def problema(dominio, instancia):
    """Objeto con la interfaz del curso: initial, actions, result, is_goal, step_cost."""
    if dominio == "8puzzle":
        return search.EightPuzzle(tuple(instancia))
    if dominio == "grid":
        return gridworld.GridProblem(instancia)
    raise ValueError(dominio)


def buscar(id_instancia):
    """Devuelve (dominio, nivel, instancia) a partir de un id como 'grid-8-03'."""
    dominio, nivel, i = id_instancia.rsplit("-", 2)
    return dominio, int(nivel), banco(dominio)[int(nivel)][int(i)]
