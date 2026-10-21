"""Validator. Es determinista y nunca le pregunta nada al modelo. Para cada respuesta revisa:
1. El camino es legal? (pasos entre casillas vecinas, dentro del tablero, empieza en el inicio y termina en la meta). Los grids de la Semana 4 no tienen paredes.
2. El costo reportado esta bien sumado? (igual al costo que recalculamos)
3. El camino es optimo? (costo recalculado == costo óptimo de A*)

Categoria principal:
  optimal_correct     legal, optimo y con el costo bien reportado (acierto)
  illegal_path        1.camino ilegal
  legal_suboptimal    2.legal pero subóptimo (sin importar el costo que reportó)
  optimal_wrong_cost  3.legal y optimo, pero con el costo mal reportado
Categorías extra, contadas aparte:
  unparseable         no hay JSON o el camino no tiene el formato pedido
  timeout             la llamada al modelo falló o tardó demasiado

Para cada camino legal también se guarda `cost_reported_ok`, para saber cuántas veces un camino subóptimo además venía con el costo mal sumado
"""
import json

from duel_problems import cell_cost, find_cell, step8
from gridworld import TERRAIN
from search import GOAL as GOAL8

OK = "optimal_correct"
ILLEGAL = "illegal_path"
SUBOPT = "legal_suboptimal"
BADCOST = "optimal_wrong_cost"
NOANSWER = "unparseable"
TIMEOUT = "timeout"
CATEGORIES = [OK, ILLEGAL, SUBOPT, BADCOST, NOANSWER, TIMEOUT]


#parsing
def _json_objects(text):
    dec = json.JSONDecoder()
    i = 0
    while True:
        i = text.find("{", i)
        if i == -1:
            return
        try:
            obj, end = dec.raw_decode(text[i:])
            if isinstance(obj, dict):
                yield obj
            i += max(end, 1)
        except json.JSONDecodeError:
            i += 1


def parse_answer(text):
    """Last JSON object in the text that has a 'path' key, else None."""
    found = None
    for obj in _json_objects(text or ""):
        if "path" in obj:
            found = obj
    return found


def parse_tool_call(text):
    """Last JSON object with a 'tool' key, else None."""
    found = None
    for obj in _json_objects(text or ""):
        if "tool" in obj:
            found = obj
    return found


def _parse_moves(path):
    if isinstance(path, list):
        path = "".join(str(x) for x in path)
    if not isinstance(path, str):
        return None
    s = "".join(ch for ch in path.upper() if ch not in " ,;-\t\n>[]'\"")
    if s and set(s) <= set("UDLR"):
        return s
    return None


def _parse_cells(path):
    if not isinstance(path, list) or not path:
        return None
    cells = []
    for p in path:
        if (isinstance(p, (list, tuple)) and len(p) == 2
                and all(isinstance(v, (int, float)) and float(v).is_integer() for v in p)):
            cells.append((int(p[0]), int(p[1])))
        else:
            return None
    return cells


def normalized_path(domain, answer):
    """Canonical string of the answer's path (for counting distinct answers)."""
    if not answer:
        return ""
    if domain == "8puzzle":
        return _parse_moves(answer.get("path")) or f"UNPARSEABLE:{answer.get('path')!r}"
    cells = _parse_cells(answer.get("path"))
    return "->".join(f"{r},{c}" for r, c in cells) if cells else f"UNPARSEABLE:{answer.get('path')!r}"


def _reported_cost(answer):
    v = answer.get("cost")
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        return None
    return int(v) if float(v).is_integer() else None


#validation
def _result(category, optimal, actual=None, reported=None, detail="", cost_ok=None):
    return {"category": category, "optimal_cost": optimal, "actual_cost": actual,
            "reported_cost": reported, "cost_reported_ok": cost_ok, "detail": detail}


def _finish(actual, reported, optimal):
    cost_ok = reported is not None and reported == actual
    if actual > optimal:
        return _result(SUBOPT, optimal, actual, reported, f"cost {actual} > optimal {optimal}", cost_ok)
    if actual < optimal:  #impossible unless the reference solver is wrong
        return _result(ILLEGAL, optimal, actual, reported, "cost below proven optimum: reference bug?", cost_ok)
    if not cost_ok:
        return _result(BADCOST, optimal, actual, reported, f"reported {reported}, actual {actual}", cost_ok)
    return _result(OK, optimal, actual, reported, "", True)


def validate_8puzzle(inst, answer):
    opt = inst["optimal_cost"]
    moves = _parse_moves(answer.get("path"))
    if moves is None:
        return _result(NOANSWER, opt, detail=f"path not a UDLR string: {answer.get('path')!r}")
    reported = _reported_cost(answer)
    state = tuple(inst["start"])
    for i, m in enumerate(moves):
        state = step8(state, m)
        if state is None:
            return _result(ILLEGAL, opt, reported=reported, detail=f"move {i+1} ({m}) leaves the board")
    if state != GOAL8:
        return _result(ILLEGAL, opt, reported=reported, detail="path does not end at the goal")
    return _finish(len(moves), reported, opt)


def validate_grid(inst, answer):
    opt = inst["optimal_cost"]
    rows = inst["rows"]
    cells = _parse_cells(answer.get("path"))
    if cells is None:
        return _result(NOANSWER, opt, detail=f"path not a list of [r,c]: {answer.get('path')!r}"[:200])
    reported = _reported_cost(answer)
    R, C = len(rows), len(rows[0])
    start, goal = find_cell(rows, "S"), find_cell(rows, "G")
    if cells[0] != start:
        return _result(ILLEGAL, opt, reported=reported, detail=f"does not start at S {start}")
    if cells[-1] != goal:
        return _result(ILLEGAL, opt, reported=reported, detail=f"does not end at G {goal}")
    actual = 0
    for i, (r, c) in enumerate(cells):
        if not (0 <= r < R and 0 <= c < C):
            return _result(ILLEGAL, opt, reported=reported, detail=f"cell {i} {(r, c)} out of bounds")
        if rows[r][c] not in TERRAIN:  #the Week 4 grids have no walls; kept for safety
            return _result(ILLEGAL, opt, reported=reported, detail=f"cell {i} {(r, c)} is not walkable")
        if i > 0:
            pr, pc = cells[i - 1]
            if abs(r - pr) + abs(c - pc) != 1:
                return _result(ILLEGAL, opt, reported=reported, detail=f"step {i} {(pr, pc)}->{(r, c)} is not adjacent")
            actual += cell_cost(rows[r][c])
    return _finish(actual, reported, opt)


def validate(inst, answer, arm_error=None):
    """answer: dict from parse_answer, or None. arm_error='timeout' for backend failures."""
    if arm_error == "timeout":
        return _result(TIMEOUT, inst["optimal_cost"], detail="backend call failed / timed out")
    if answer is None:
        return _result(NOANSWER, inst["optimal_cost"], detail="no JSON answer with a 'path' key")
    if inst["domain"] == "8puzzle":
        return validate_8puzzle(inst, answer)
    return validate_grid(inst, answer)
