"""Pruebas de la base (motor CSP, formato de problemas, CSV). Deben pasar siempre.

    python code/tests/test_base.py
"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from csp_motor import ErrorModelo, resolver  # noqa: E402
from problemas import calificar, ejemplos  # noqa: E402
from resultados import COLUMNAS, escribir, fila_vacia, leer  # noqa: E402


def _modelo(restricciones, n=3, nombres=("A", "B", "C")):
    return {"variables": {v: list(range(1, n + 1)) for v in nombres},
            "constraints": [{"type": "alldiff", "vars": list(nombres)}] + restricciones}


def test_unica():
    r = resolver(_modelo([{"type": "eq", "a": "A", "b": 1}, {"type": "neq", "a": "C", "b": 2}]))
    assert r.estado == "unica" and r.solucion == {"A": 1, "B": 2, "C": 3}


def test_sub_restringido_se_detecta():
    r = resolver(_modelo([{"type": "eq", "a": "A", "b": 1}]))
    assert r.estado == "multiple" and r.n_soluciones == 2


def test_sobre_restringido_se_detecta():
    r = resolver(_modelo([{"type": "eq", "a": "A", "b": 1}, {"type": "eq", "a": "B", "b": 1}]))
    assert r.estado == "sin_solucion"


def test_relaciones_numericas():
    r = resolver(_modelo([{"type": "offset", "a": "B", "b": "A", "k": 1},
                          {"type": "offset", "a": "C", "b": "B", "k": 1}]))
    assert r.solucion == {"A": 1, "B": 2, "C": 3}
    r = resolver(_modelo([{"type": "lt", "a": "C", "b": "A"}, {"type": "gt", "a": "B", "b": "A"}]))
    assert r.estado == "unica" and r.solucion == {"A": 2, "B": 3, "C": 1}
    r = resolver(_modelo([{"type": "lt", "a": "C", "b": "A"}, {"type": "gt", "a": "B", "b": "A"},
                          {"type": "adj", "a": "C", "b": "B"}]))
    assert r.estado == "sin_solucion"        # C=1 y B=3 no están juntos


def test_errores_de_construccion():
    casos = [
        ({"constraints": []}, "sintaxis"),
        ({"variables": {"A": [1, 2]}, "constraints": [{"type": "mayor", "a": "A", "b": 1}]}, "sintaxis"),
        (_modelo([{"type": "eq", "a": "Z", "b": 1}]), "aridad_alcance"),
        (_modelo([{"type": "eq", "a": "A", "b": "Bob"}]), "aridad_alcance"),
        (_modelo([{"type": "offset", "a": "A", "b": "B"}]), "aridad_alcance"),
        ({"variables": {"X": ["rojo", "azul"], "Y": ["rojo", "azul"]},
          "constraints": [{"type": "lt", "a": "X", "b": "Y"}]}, "aridad_alcance"),
    ]
    for modelo, esperado in casos:
        try:
            resolver(modelo)
        except ErrorModelo as e:
            assert e.categoria == esperado, (modelo, e.categoria)
        else:
            raise AssertionError(f"debió fallar: {modelo}")


def test_timeout():
    nombres = [f"V{i}" for i in range(12)]
    m = {"variables": {v: list(range(11)) for v in nombres},
         "constraints": [{"type": "alldiff", "vars": nombres}]}   # 12 variables, 11 valores: no hay solución
    r = resolver(m, limite_llamadas=500)
    assert r.estado == "timeout"


def test_ejemplos_y_calificar():
    ex = ejemplos()
    assert len(ex) == 3
    for p in ex:
        r = resolver(p["modelo_mano"])
        assert r.estado == "unica"
        assert calificar(p, r.solucion)[0] == "correcto"
    p = ex[0]
    malo = dict(p["gold"])
    malo["Ana"] = 1
    assert calificar(p, malo)[0] == "incorrecto"
    assert calificar(p, None)[0] == "sin_respuesta"
    assert calificar(p, {" ana ": "3", **{k: v for k, v in p["gold"].items() if k != "Ana"}})[0] == "correcto"


def test_csv_ida_y_vuelta():
    with tempfile.TemporaryDirectory() as d:
        escribir([fila_vacia(problema_id="x", brazo="A", resultado="correcto")], "brazo_a.csv", d)
        filas = leer(carpeta=d)
        assert list(filas[0]) == COLUMNAS and filas[0]["resultado"] == "correcto"


if __name__ == "__main__":
    pruebas = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in pruebas:
        t()
        print(f"ok  {t.__name__}")
    print(f"{len(pruebas)} pruebas de la base pasan")
