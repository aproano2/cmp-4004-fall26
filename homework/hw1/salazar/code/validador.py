"""Validador propio de respuestas (Parte 2). Diseño: Jalil Chano;
integrado al motor y a los bancos del grupo.

Regla del enunciado: NUNCA se le pregunta al modelo si su respuesta es correcta.
Este archivo decide, con código nuestro, si un camino es legal, si su costo
reportado está bien calculado y si es óptimo contra A*.

El ``duel.py`` del curso (``curso/week04``) también clasifica grillas, pero no
revisa paredes ni el 8-puzzle; lo usamos solo como referencia.

Categorías (columna ``category`` de los CSV), en este orden de prioridad:
    malformed   — no se pudo extraer PATH y COST de la respuesta
    illegal     — símbolo inválido, se sale del tablero, entra a una pared '#'
                  o no termina en la meta                      (falla tipo 1)
    suboptimal  — legal, pero su costo real es mayor que el óptimo (falla tipo 2)
    wrong_cost  — legal y óptimo, pero el costo REPORTADO no es el real (falla tipo 3)
    correct     — legal, óptimo y con el costo bien reportado

Una respuesta puede ser subóptima Y tener mal el costo a la vez: ``category``
toma la primera según el orden, y las banderas ``suboptimal`` y ``wrong_cost``
permiten contar las tres fallas por separado, como pide la consigna.
"""
from __future__ import annotations

import heapq
import re
from dataclasses import dataclass
from itertools import count

from rutas import preparar_rutas

preparar_rutas()
import dominios  # noqa: E402
import heuristicas  # noqa: E402
import motor  # noqa: E402
from gridworld import TERRAIN  # noqa: E402
from search import GOAL  # noqa: E402

CATEGORIAS = ("malformed", "illegal", "suboptimal", "wrong_cost", "correct")
PARED = "#"           # las grillas del curso no tienen paredes, pero se valida igual
MOV = {"U": (-1, 0), "D": (1, 0), "L": (0, -1), "R": (0, 1)}


@dataclass
class Veredicto:
    category: str               # una de CATEGORIAS
    reason: str                 # detalle legible: "paso 7: se sale del tablero con U"
    path: str | None            # camino tal como lo entendimos
    reported_cost: int | None   # lo que dijo el modelo
    checker_cost: int | None    # lo que cuesta de verdad (None si es ilegal)
    optimal_cost: int | None    # óptimo según nuestro A* con heurística admisible
    suboptimal: bool = False    # falla tipo 2 (aunque category diga otra cosa)
    wrong_cost: bool = False    # falla tipo 3 (aunque category diga otra cosa)
    tolerant: bool = False      # hubo que usar la lectura tolerante


# ---- lectura de la respuesta ---------------------------------------------------------
# Estricta: exactamente el formato que pide el prompt del curso,
# "PATH: <letras, sin separadores>" y "COST: <entero>". Se toma la última aparición.
_PATH_E = re.compile(r"^PATH:[ \t]*([A-Z]*)[ \t]*$", re.M)
_COST_E = re.compile(r"^COST:[ \t]*(\d+)[ \t]*$", re.M)
# Tolerante (como en week 5): mayúsculas/minúsculas, markdown, comas, espacios,
# flechas y corchetes ("PATH: U, R, D", "**path:** [u -> r]", "cost = 4").
_PATH_T = re.compile(r"PATH\s*[:=]\s*([^\n]*)", re.I)
_COST_T = re.compile(r"COST\s*[:=]\s*(\d+)", re.I)


def extraer_detallado(texto: str | None):
    """(camino, costo, tolerante). (None, None, False) si falta PATH o COST.

    Los símbolos del camino NO se filtran: una letra que no sea U/D/L/R la
    detecta el recorrido y la respuesta cuenta como illegal, no como malformed."""
    if not texto:
        return None, None, False
    p, c = _PATH_E.findall(texto), _COST_E.findall(texto)
    if p and c:
        return p[-1], int(c[-1]), False
    limpio = texto.replace("*", "").replace("`", "")
    p, c = _PATH_T.findall(limpio), _COST_T.findall(limpio)
    if not p or not c:
        return None, None, False
    camino = re.sub(r"[,\[\]'\"\->\s.]", "", p[-1].upper())
    return camino, int(c[-1]), True


def extraer_respuesta(texto: str | None):
    """(camino, costo) desde el texto del modelo; (None, None) si no se puede."""
    camino, costo, _ = extraer_detallado(texto)
    return camino, costo


# ---- recorrido ----------------------------------------------------------------------

def recorrer_grid(grid, camino: str):
    """Camina desde S. Devuelve (estado_final, costo_real, motivo_error).

    El costo se cobra al ENTRAR a cada celda (TERRAIN del curso)."""
    prob_filas, ncols = len(grid), len(grid[0])
    r, c = next((i, fila.index("S")) for i, fila in enumerate(grid) if "S" in fila)
    total = 0
    for i, m in enumerate(camino, 1):
        if m not in MOV:
            return None, None, f"paso {i}: símbolo inválido {m!r} (solo U/D/L/R)"
        r, c = r + MOV[m][0], c + MOV[m][1]
        if not (0 <= r < prob_filas and 0 <= c < ncols):
            return None, None, f"paso {i}: se sale del tablero con {m}"
        if grid[r][c] == PARED:
            return None, None, f"paso {i}: entra a una pared en ({r},{c})"
        total += TERRAIN[grid[r][c]]
    return (r, c), total, None


def recorrer_puzzle(estado, camino: str):
    """Aplica movimientos del BLANCO (U/D/L/R). Cada movimiento cuesta 1."""
    s = list(estado)
    for i, m in enumerate(camino, 1):
        if m not in MOV:
            return None, None, f"paso {i}: símbolo inválido {m!r} (solo U/D/L/R)"
        b = s.index(0)
        r, c = divmod(b, 3)
        r, c = r + MOV[m][0], c + MOV[m][1]
        if not (0 <= r < 3 and 0 <= c < 3):
            return None, None, f"paso {i}: el blanco se sale del tablero con {m}"
        j = r * 3 + c
        s[b], s[j] = s[j], s[b]
    return tuple(s), len(camino), None


# ---- óptimo de referencia -------------------------------------------------------------
_OPTIMOS = {}


def _ucs_con_paredes(grid):
    """Respaldo para grillas con '#', que el GridProblem del curso no conoce:
    UCS con las mismas reglas del recorrido (diseño de Jalil)."""
    ini = next((i, f.index("S")) for i, f in enumerate(grid) if "S" in f)
    meta = next((i, f.index("G")) for i, f in enumerate(grid) if "G" in f)
    tie, heap, mejor = count(), [(0, 0, ini)], {ini: 0}
    while heap:
        g, _, (r, c) = heapq.heappop(heap)
        if (r, c) == meta:
            return g
        if g > mejor[(r, c)]:
            continue
        for dr, dc in MOV.values():
            r2, c2 = r + dr, c + dc
            if 0 <= r2 < len(grid) and 0 <= c2 < len(grid[0]) and grid[r2][c2] != PARED:
                g2 = g + TERRAIN[grid[r2][c2]]
                if g2 < mejor.get((r2, c2), float("inf")):
                    mejor[(r2, c2)] = g2
                    heapq.heappush(heap, (g2, next(tie), (r2, c2)))
    return None


def costo_optimo(dominio, instancia) -> int | None:
    """Óptimo con NUESTRO A* (motor.resolver + Manhattan admisible), en caché."""
    clave = (dominio, tuple(instancia))
    if clave not in _OPTIMOS:
        if dominio == "grid" and any(PARED in f for f in instancia):
            _OPTIMOS[clave] = _ucs_con_paredes(instancia)
        else:
            h = heuristicas.registro()[dominio]["manhattan"]
            r = motor.resolver(dominios.problema(dominio, instancia), "astar", h=h,
                               timeout_s=300)
            _OPTIMOS[clave] = int(r.cost) if r.status == "solved" else None
    return _OPTIMOS[clave]


# ---- clasificación --------------------------------------------------------------------

def validar(dominio, instancia, camino: str | None, costo_reportado: int | None,
            tolerante: bool = False) -> Veredicto:
    """Clasifica una respuesta: malformed -> illegal -> suboptimal -> wrong_cost -> correct.

    La legalidad se revisa ANTES de pedir el óptimo (el GridProblem del curso no
    conoce '#')."""
    # extraer_detallado ya devuelve (None, None) si falta PATH o COST en el texto.
    # Si alguien llama con un camino y sin costo, se evalúa el camino igual.
    if camino is None:
        return Veredicto("malformed", "no se pudo leer PATH y COST", camino,
                         costo_reportado, None, None, tolerant=tolerante)
    if dominio == "grid":
        final, real, motivo = recorrer_grid(instancia, camino)
        meta = next((i, f.index("G")) for i, f in enumerate(instancia) if "G" in f)
    else:
        final, real, motivo = recorrer_puzzle(instancia, camino)
        meta = GOAL
    if motivo is None and final != meta:
        motivo = "el camino termina fuera de la meta"
    if motivo:
        return Veredicto("illegal", motivo, camino, costo_reportado, None, None,
                         tolerant=tolerante)
    opt = costo_optimo(dominio, instancia)
    sub = opt is not None and real > opt
    mal = costo_reportado != real
    if sub:
        cat, motivo = "suboptimal", f"cuesta {real}, el óptimo es {opt}"
    elif mal:
        cat, motivo = "wrong_cost", f"reportó {costo_reportado}, en realidad cuesta {real}"
    else:
        cat, motivo = "correct", ""
    if sub and mal:
        motivo += f"; además reportó {costo_reportado}"
    return Veredicto(cat, motivo, camino, costo_reportado, real, opt,
                     suboptimal=sub, wrong_cost=mal, tolerant=tolerante)


def validar_texto(dominio, instancia, texto: str | None) -> Veredicto:
    """Atajo: extrae PATH/COST del texto del modelo y valida."""
    camino, costo, tol = extraer_detallado(texto)
    return validar(dominio, instancia, camino, costo, tolerante=tol)
