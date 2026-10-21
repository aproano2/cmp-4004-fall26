"""Pruebas de aceptación de validador.py.

    python code/tests/test_validador.py
Usan respuestas construidas a mano: prueban el validador, NO la calidad del LLM.
Puedes AGREGAR pruebas; no borres ni debilites estas.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rutas import preparar_rutas  # noqa: E402

preparar_rutas()
import dominios  # noqa: E402
import motor  # noqa: E402
import validador as V  # noqa: E402

GRID = dominios.banco("grid")[5][0]     # .S... / ..~~~ / ~..,G / .~~,. / .,~..


def _optimo_grid(grid):
    r = motor.resolver(dominios.problema("grid", grid), "ucs")
    return "".join(r.path), int(r.cost)


def test_grid_correcto_y_costo_mal_reportado():
    camino, costo = _optimo_grid(GRID)
    assert V.validar("grid", GRID, camino, costo).category == "correct"
    v = V.validar("grid", GRID, camino, costo + 1)
    assert v.category == "wrong_cost" and v.checker_cost == costo


def test_grid_suboptimo():
    camino, costo = _optimo_grid(GRID)
    # ida y vuelta extra: sigue siendo legal pero cuesta más
    largo = "LR" + camino if GRID[1][0] != "#" else "DU" + camino
    v = V.validar("grid", GRID, largo, None)
    assert v.category == "suboptimal" and v.checker_cost > v.optimal_cost == costo


def test_grid_ilegales():
    assert V.validar("grid", GRID, "UUUU", 4).category == "illegal"     # sale por arriba
    assert V.validar("grid", GRID, "R", 1).category == "illegal"        # no llega a G
    assert V.validar("grid", GRID, "RXR", 2).category == "illegal"      # símbolo inválido


def test_grid_con_pared():
    camino, costo = _optimo_grid(GRID)
    fila, col = dominios.problema("grid", GRID).initial
    paso = {"U": (-1, 0), "D": (1, 0), "L": (0, -1), "R": (0, 1)}[camino[0]]
    r, c = fila + paso[0], col + paso[1]
    con_pared = [list(f) for f in GRID]
    con_pared[r][c] = "#"
    con_pared = ["".join(f) for f in con_pared]
    assert V.validar("grid", con_pared, camino, costo).category == "illegal"


def test_malformed():
    assert V.extraer_respuesta("no sé") == (None, None)
    assert V.validar("grid", GRID, None, None).category == "malformed"


def test_extraer_formato_pedido():
    assert V.extraer_respuesta("blah\nPATH: RRDD\nCOST: 12\n") == ("RRDD", 12)


def test_puzzle():
    s = (1, 2, 3, 4, 5, 6, 7, 0, 8)          # el blanco va a la derecha: "R"
    assert V.validar("8puzzle", s, "R", 1).category == "correct"
    assert V.validar("8puzzle", s, "R", 2).category == "wrong_cost"
    assert V.validar("8puzzle", s, "LRR", 3).category == "suboptimal"
    assert V.validar("8puzzle", s, "D", 1).category == "illegal"     # sale del tablero


# ---- lectura tolerante y fallas combinadas ----------------------------------------------

def test_lectura_estricta_y_tolerante():
    assert V.extraer_detallado("PATH: DDRR\nCOST: 4") == ("DDRR", 4, False)
    assert V.extraer_detallado("PATH: D, D, R, R\nCOST: 4") == ("DDRR", 4, True)
    assert V.extraer_detallado("**PATH:** d -> r\ncost = 4") == ("DR", 4, True)
    assert V.extraer_respuesta("PATH: DDRR") == (None, None)          # falta COST


def test_suboptimo_y_costo_mal_a_la_vez():
    camino, costo = _optimo_grid(GRID)
    v = V.validar("grid", GRID, "LR" + camino, costo)                  # cuesta más y dice el óptimo
    assert v.category == "suboptimal" and v.suboptimal and v.wrong_cost


if __name__ == "__main__":
    pruebas = [v for k, v in dict(globals()).items() if k.startswith("test_")]
    fallas = 0
    for t in pruebas:
        try:
            t()
            print(f"  ok    {t.__name__}")
        except NotImplementedError:
            fallas += 1
            print(f"  TODO  {t.__name__} (falta implementar)")
        except AssertionError as e:
            fallas += 1
            print(f"  FALLA {t.__name__}: {e}")
    print(f"{len(pruebas) - fallas}/{len(pruebas)} pasan")
    sys.exit(1 if fallas else 0)
