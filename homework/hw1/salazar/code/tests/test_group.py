"""Pruebas de la base compartida (motor, dominios, timeout).

Correr desde la carpeta del grupo:  python code/tests/test_group.py
(también funciona con pytest). Deben pasar SIEMPRE antes de hacer commit.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rutas import preparar_rutas  # noqa: E402

preparar_rutas()
import dominios  # noqa: E402
import gridworld  # noqa: E402
import motor  # noqa: E402
import search  # noqa: E402


def test_bancos_completos():
    for dom in dominios.DOMINIOS:
        ids = [i for i, _, _ in dominios.instancias(dom)]
        assert len(ids) == 40 and len(set(ids)) == 40, dom
    assert dominios.buscar("grid-8-03")[2] == dominios.banco("grid")[8][3]


def test_mismas_expansiones_que_search_del_curso():
    # Nuestro motor agrega métricas, pero debe expandir EXACTAMENTE igual.
    casos = [("8puzzle", lvl) for lvl in (4, 8, 12)] + [("grid", s) for s in (5, 8)]
    for dom, nivel in casos:
        for inst in dominios.banco(dom)[nivel][:3]:
            for alg, tipo in (("bfs", "fifo"), ("dfs", "lifo"), ("ucs", "priority")):
                nodo, exp = search.search(dominios.problema(dom, inst), tipo)
                r = motor.resolver(dominios.problema(dom, inst), alg)
                assert r.status == "solved"
                assert (r.expansions, r.cost) == (exp, nodo.g), (dom, nivel, alg)


def test_bfs_suboptimo_y_ucs_optimo_en_tinygraph():
    tiny = search.TinyGraph("start", "A")
    assert motor.resolver(tiny, "bfs").cost == 10
    assert motor.resolver(tiny, "ucs").cost == 2
    assert motor.resolver(tiny, "astar", h=lambda p, s: 0).cost == 2


def test_astar_h0_igual_a_ucs_y_al_astar_del_curso():
    for grid in dominios.banco("grid")[8]:
        ucs = motor.resolver(gridworld.GridProblem(grid), "ucs")
        a0 = motor.resolver(gridworld.GridProblem(grid), "astar", h=lambda p, s: 0)
        curso, _ = gridworld.astar(gridworld.GridProblem(grid), lambda p, s: 0)
        assert ucs.cost == a0.cost == curso.g


def test_ids_longitud_optima_en_8puzzle():
    for nivel in (4, 8):
        for inst in dominios.banco("8puzzle")[nivel][:3]:
            r = motor.resolver(dominios.problema("8puzzle", inst), "ids")
            assert r.status == "solved" and r.length == nivel


def test_timeout_se_reporta_como_timeout():
    inst = dominios.banco("8puzzle")[16][0]
    r = motor.resolver(dominios.problema("8puzzle", inst), "ids", timeout_s=0.01)
    assert r.status == "timeout" and r.cost is None and r.expansions > 0


def test_frontera_maxima_positiva():
    r = motor.resolver(dominios.problema("grid", dominios.banco("grid")[5][0]), "bfs")
    assert r.max_frontier >= 1


def test_b_estrella():
    from analisis_optimalidad import b_estrella
    assert abs(b_estrella(3, 3) - 1) < 1e-6          # cadena: N = d  ->  b* = 1
    assert abs(b_estrella(14, 3) - 2) < 1e-6         # 1 + 2 + 4 + 8 = 15 = N + 1
    assert b_estrella(10, 0) is None


def test_herramienta_devuelve_caminos_que_el_validador_acepta():
    # La herramienta del brazo LLM+A* debe responder en U/D/L/R en ambos dominios.
    import herramienta
    import validador
    for dom in dominios.DOMINIOS:
        for id_, _, inst in dominios.instancias(dom, por_nivel=2):
            clave = "state" if dom == "8puzzle" else "grid"
            out, _ = herramienta.ejecutar_herramienta(
                {"tool": "astar", "domain": dom, clave: list(inst)}, dom)
            v = validador.validar(dom, inst, out["path"], out["cost"])
            assert v.category == "correct", (id_, out)


if __name__ == "__main__":
    pruebas = [v for k, v in dict(globals()).items() if k.startswith("test_")]
    for t in pruebas:
        t()
        print(f"  ok  {t.__name__}")
    print(f"{len(pruebas)} pruebas de la base pasan")
