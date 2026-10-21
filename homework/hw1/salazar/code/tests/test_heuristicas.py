"""Pruebas de aceptación de heuristicas.py.

    python code/tests/test_heuristicas.py
Puedes AGREGAR pruebas; no borres ni debilites estas.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rutas import preparar_rutas  # noqa: E402

preparar_rutas()
import dominios  # noqa: E402
import heuristicas as H  # noqa: E402
import motor  # noqa: E402

UNO_DE_LA_META = (1, 2, 3, 4, 5, 6, 7, 0, 8)


def _p(estado):
    return dominios.problema("8puzzle", estado)


def test_ejemplos_8puzzle():
    assert H.h_misplaced(_p(UNO_DE_LA_META), UNO_DE_LA_META) == 1
    assert H.h_manhattan_puzzle(_p(UNO_DE_LA_META), UNO_DE_LA_META) == 1
    meta = (1, 2, 3, 4, 5, 6, 7, 8, 0)
    assert H.h_misplaced(_p(meta), meta) == 0 == H.h_manhattan_puzzle(_p(meta), meta)


def test_admisibles_en_el_banco_8puzzle():
    # El nivel ES el costo óptimo (verificado por el profe con BFS exhaustivo).
    for id_, nivel, s in dominios.instancias("8puzzle"):
        assert H.h_misplaced(_p(s), s) <= nivel, id_
        assert H.h_manhattan_puzzle(_p(s), s) <= nivel, id_


def test_manhattan_domina_misplaced_estado_por_estado():
    for _, _, s in dominios.instancias("8puzzle"):
        assert H.h_manhattan_puzzle(_p(s), s) >= H.h_misplaced(_p(s), s)


def test_manhattan_grid_admisible():
    for id_, _, g in dominios.instancias("grid"):
        prob = dominios.problema("grid", g)
        optimo = motor.resolver(prob, "ucs").cost
        assert H.h_manhattan_grid(prob, prob.initial) <= optimo, id_
        assert H.h_manhattan_grid(prob, prob.goal) == 0


def test_astar_admisible_da_el_optimo():
    for dom, nombre in (("8puzzle", "manhattan"), ("8puzzle", "misplaced"), ("grid", "manhattan")):
        h = H.registro()[dom][nombre]
        for id_, _, inst in dominios.instancias(dom, niveles=dominios.NIVELES[dom][:3], por_nivel=3):
            ucs = motor.resolver(dominios.problema(dom, inst), "ucs")
            a = motor.resolver(dominios.problema(dom, inst), "astar", h=h)
            assert a.cost == ucs.cost, (id_, nombre)


def test_inflar():
    h3 = H.inflar(H.h_manhattan_puzzle, 3)
    s = dominios.banco("8puzzle")[8][0]
    assert h3(_p(s), s) == 3 * H.h_manhattan_puzzle(_p(s), s)
    assert h3.__name__.endswith("_x3")
    assert set(H.registro()["8puzzle"]) == {"misplaced", "manhattan", "manhattan_x3"}


def test_admisibles_y_consistentes_en_los_181440_estados():
    # Garantía completa: BFS desde la meta da h* de cada estado alcanzable.
    from admisibilidad_exhaustiva import comprobar
    for f in comprobar():
        assert f["estados"] == 181440
        assert f["sobreestima"] == 0 and f["inconsistente"] == 0, f
        assert f["manhattan_no_domina"] == 0, f


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
