"""Parte 1, análisis 1 y 4. Autoría: Daniel Salazar.

Análisis 1: comprobamos en las 80 instancias que UCS y A* con heurística
admisible devuelven el MISMO costo, y que BFS no lo hace cuando los costos no
son uniformes (grilla). Mostramos la instancia donde BFS queda más lejos del
óptimo, con los dos caminos dibujados. En el 8-puzzle todos los pasos cuestan 1
y BFS sí es óptimo: lo decimos con esa condición.

Análisis 4: factor de ramificación efectivo b* de A* con cada heurística, con
N = expansiones y d = longitud de la solución:

    N + 1 = 1 + b* + b*^2 + ... + b*^d          (resuelto por bisección)

Usamos UCS (A* con h = 0) como referencia sin heurística.

Solo lee results/parte1_mediciones.csv; para dibujar caminos vuelve a correr
UCS y BFS sobre UNA instancia (son deterministas, dan el mismo resultado).

Salidas:
    results/optimalidad.csv     una fila por instancia: costo de cada config
    results/bfs_suboptimo.md    la instancia elegida, dibujada
    results/branching.csv       b* por instancia y config
    results/branching_resumen.csv  mediana [q1, q3] de b* por dominio, nivel y config
    fig/branching.png

Uso:  python code/analisis_optimalidad.py [--entrada otro.csv] [--salida carpeta]
"""
from __future__ import annotations

import argparse
from pathlib import Path

from rutas import FIG, RESULTS, preparar_rutas

preparar_rutas()
import dominios  # noqa: E402
import motor  # noqa: E402
from estadistica import agrupar, escribir_csv, leer_csv, mediana_iqr  # noqa: E402

ADMISIBLES = ("A*-misplaced", "A*-manhattan")      # x3 NO es admisible a propósito
REFERENCIA_BSTAR = ("UCS",) + ADMISIBLES + ("A*-manhattan_x3",)


# ---- análisis 4: b* ----------------------------------------------------------------

def b_estrella(n_expansiones, profundidad, tol=1e-9):
    """b* tal que 1 + b + b^2 + ... + b^d = N + 1. None si d = 0 o N = 0.

    El lado izquierdo crece con b, así que la bisección converge. Con N = d el
    árbol es una cadena y b* = 1.
    """
    n, d = n_expansiones, profundidad
    if not d or not n:
        return None
    objetivo = n + 1

    def total(b):
        return d + 1 if b == 1 else (b ** (d + 1) - 1) / (b - 1)

    lo, hi = 1e-9, max(2.0, float(n))
    while total(hi) < objetivo:
        hi *= 2
    while hi - lo > tol:
        mid = (lo + hi) / 2
        if total(mid) < objetivo:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


# ---- análisis 1: optimalidad -------------------------------------------------------

def tabla_optimalidad(filas):
    """Una fila por instancia con el costo de cada config y las comparaciones."""
    configs = sorted({f["config"] for f in filas})
    out = []
    for (dom, nivel, inst), grupo in agrupar(filas, "domain", "level", "instance").items():
        costo = {f["config"]: (f["cost"] if f["status"] == "solved" else None) for f in grupo}
        estado = {f["config"]: f["status"] for f in grupo}
        ucs = costo.get("UCS")
        fila = {"domain": dom, "level": nivel, "instance": inst}
        for c in configs:
            fila[f"cost_{c}"] = costo.get(c) if estado.get(c) == "solved" else estado.get(c, "")
        fila["astar_admisible_igual_ucs"] = all(
            costo.get(c) == ucs for c in ADMISIBLES if c in costo) if ucs is not None else ""
        fila["admisibles_medidos"] = "+".join(c for c in ADMISIBLES if c in costo)
        bfs = costo.get("BFS")
        fila["bfs_sobrecosto"] = (bfs - ucs) if None not in (bfs, ucs) else ""
        out.append(fila)
    return out


def _dibujar(grid, camino):
    """Grilla con el camino marcado con '*' (sin tocar S y G)."""
    prob = dominios.problema("grid", grid)
    celdas = [list(f) for f in grid]
    r, c = prob.initial
    for a in camino:
        dr, dc = {"U": (-1, 0), "D": (1, 0), "L": (0, -1), "R": (0, 1)}[a]
        r, c = r + dr, c + dc
        if celdas[r][c] not in "SG":
            celdas[r][c] = "*"
    return "\n".join(" ".join(f) for f in celdas)


def informe_bfs(tabla, ruta):
    """Elige la instancia de grilla con mayor sobrecosto de BFS y la documenta."""
    grid_rows = [f for f in tabla if f["domain"] == "grid" and f["bfs_sobrecosto"] != ""]
    sub = [f for f in grid_rows if f["bfs_sobrecosto"] > 0]
    puzzle = [f for f in tabla if f["domain"] == "8puzzle" and f["bfs_sobrecosto"] != ""]
    lineas = ["# BFS con costos no uniformes", ""]
    lineas.append(
        f"BFS devolvió un camino más caro que el óptimo (UCS) en {len(sub)} de "
        f"{len(grid_rows)} grillas. En el 8-puzzle, donde todo paso cuesta 1, el "
        f"sobrecosto de BFS fue 0 en {sum(f['bfs_sobrecosto'] == 0 for f in puzzle)} de "
        f"{len(puzzle)} instancias: BFS es óptimo solo cuando los costos son uniformes.")
    lineas.append("")
    lineas.append("| nivel | grillas | BFS subóptimo | sobrecosto mediano (cuando lo hay) |")
    lineas.append("|---|---|---|---|")
    for nivel in dominios.NIVELES["grid"]:
        g = [f for f in grid_rows if f["level"] == nivel]
        s = [f["bfs_sobrecosto"] for f in g if f["bfs_sobrecosto"] > 0]
        med = mediana_iqr(s)[0]
        lineas.append(f"| {nivel}×{nivel} | {len(g)} | {len(s)} | "
                      f"{'' if med is None else f'{med:g}'} |")
    if sub:
        peor = max(sub, key=lambda f: (f["bfs_sobrecosto"] / f["cost_UCS"], -f["level"]))
        _, _, grid = dominios.buscar(peor["instance"])
        bfs = motor.resolver(dominios.problema("grid", grid), "bfs")
        ucs = motor.resolver(dominios.problema("grid", grid), "ucs")
        lineas += ["", f"## La instancia que mostramos: `{peor['instance']}`", "",
                   f"BFS usa {bfs.length} pasos y cuesta {bfs.cost:g}; UCS usa "
                   f"{ucs.length} pasos y cuesta {ucs.cost:g} "
                   f"(+{bfs.cost - ucs.cost:g}, {100 * (bfs.cost / ucs.cost - 1):.0f} % más caro). "
                   "BFS minimiza el número de pasos y no mira el terreno; UCS minimiza "
                   "el costo acumulado. Costos al entrar: `.`=1, `,`=3, `~`=8.", "",
                   f"**BFS** — `{''.join(bfs.path)}`", "", "```", _dibujar(grid, bfs.path), "```", "",
                   f"**UCS (óptimo)** — `{''.join(ucs.path)}`", "", "```",
                   _dibujar(grid, ucs.path), "```"]
    Path(ruta).write_text("\n".join(lineas) + "\n", encoding="utf-8")


# ---- análisis 4: tabla y figura ----------------------------------------------------

def _redondear(x, cifras=4):
    return None if x is None else round(x, cifras)


def tabla_branching(filas):
    out = []
    for f in filas:
        if f["config"] not in REFERENCIA_BSTAR or f["status"] != "solved":
            continue
        out.append({"domain": f["domain"], "level": f["level"], "instance": f["instance"],
                    "config": f["config"], "expansions": f["expansions"],
                    "depth": f["length"], "b_star": _redondear(b_estrella(f["expansions"], f["length"]))})
    return out


def resumen_branching(tabla):
    out = []
    for (dom, nivel, cfg), g in agrupar(tabla, "domain", "level", "config").items():
        med, q1, q3, n = mediana_iqr(f["b_star"] for f in g)
        out.append({"domain": dom, "level": nivel, "config": cfg, "n": n,
                    "b_star_median": med, "b_star_q1": q1, "b_star_q3": q3})
    return out


def figura_branching(resumen, ruta):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ejes = plt.subplots(1, 2, figsize=(11, 4.2))
    for eje, dom in zip(ejes, dominios.DOMINIOS):
        for cfg in REFERENCIA_BSTAR:
            pts = sorted((r["level"], r) for r in resumen
                         if r["domain"] == dom and r["config"] == cfg and r["n"])
            if not pts:
                continue
            x = [p[0] for p in pts]
            y = [p[1]["b_star_median"] for p in pts]
            err = [[p[1]["b_star_median"] - p[1]["b_star_q1"] for p in pts],
                   [p[1]["b_star_q3"] - p[1]["b_star_median"] for p in pts]]
            eje.errorbar(x, y, yerr=err, marker="o", capsize=3, label=cfg)
        eje.set_xticks(dominios.NIVELES[dom])
        eje.set_xlabel("profundidad óptima" if dom == "8puzzle" else "lado de la grilla")
        eje.set_ylabel("b* (mediana, barras = IQR)")
        eje.set_title("8-puzzle" if dom == "8puzzle" else "Grilla con terrenos")
        eje.grid(alpha=0.3)
        eje.legend(fontsize=8)
    fig.suptitle("Factor de ramificación efectivo b* (n = 10 por punto)")
    fig.tight_layout()
    fig.savefig(ruta, dpi=150)
    plt.close(fig)


# ---- eje 5 del scorecard para el sistema clásico ------------------------------------

def reproducibilidad_clasica(id_inst="grid-8-00", n=5):
    """Misma instancia que la reproducibilidad del LLM: 5 corridas de A*-manhattan.
    Se mide, no se asume: contamos caminos y costos distintos."""
    import heuristicas
    dom, _, inst = dominios.buscar(id_inst)
    h = heuristicas.registro()[dom]["manhattan"]
    filas = []
    for k in range(1, n + 1):
        r = motor.resolver(dominios.problema(dom, inst), "astar", h=h)
        filas.append({"instance": id_inst, "corrida": k, "path": "".join(r.path),
                      "cost": r.cost, "expansions": r.expansions})
    distintas = len({(f["path"], f["cost"]) for f in filas})
    for f in filas:
        f["respuestas_distintas"] = distintas
    return filas


def main(argv=None):
    ap = argparse.ArgumentParser(description="Análisis 1 (optimalidad) y 4 (b*)")
    ap.add_argument("--entrada", default=str(RESULTS / "parte1_mediciones.csv"))
    ap.add_argument("--salida", default=None,
                    help="carpeta para CSV y figura (por defecto results/ y fig/)")
    a = ap.parse_args(argv)
    res = Path(a.salida) if a.salida else RESULTS
    fig = Path(a.salida) if a.salida else FIG
    res.mkdir(parents=True, exist_ok=True)
    fig.mkdir(parents=True, exist_ok=True)

    filas = leer_csv(a.entrada)
    opt = tabla_optimalidad(filas)
    escribir_csv(res / "optimalidad.csv", opt)
    informe_bfs(opt, res / "bfs_suboptimo.md")
    bstar = tabla_branching(filas)
    escribir_csv(res / "branching.csv", bstar)
    resumen = resumen_branching(bstar)
    escribir_csv(res / "branching_resumen.csv", resumen)
    figura_branching(resumen, fig / "branching.png")
    escribir_csv(res / "reproducibilidad_clasica.csv", reproducibilidad_clasica())

    con_astar = [f for f in opt if f["admisibles_medidos"]]
    iguales = sum(f["astar_admisible_igual_ucs"] is True for f in con_astar)
    print(f"A* admisible = UCS en costo: {iguales}/{len(con_astar)} instancias "
          f"(heurísticas medidas: {sorted({f['admisibles_medidos'] for f in con_astar})})")


if __name__ == "__main__":
    main()
