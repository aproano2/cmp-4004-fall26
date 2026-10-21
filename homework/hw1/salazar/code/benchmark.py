"""Parte 1 — mediciones clásicas (base compartida, responsable: Daniel).

Corre cada configuración (algoritmo + heurística) sobre las 10 instancias de
cada uno de los 4 niveles de cada dominio y guarda UNA FILA POR CORRIDA:

    results/parte1_mediciones.csv
    results/parte1_mediciones_metadata.json  (timeout, máquina, huellas del código)

Columnas del CSV (contrato del grupo; no las renombres):
    domain, level, instance, algorithm, heuristic, config,
    status, cost, length, expansions, max_frontier, seconds, timeout_s

``config`` es el nombre que va en tablas y figuras: BFS, DFS, UCS, IDS,
A*-misplaced, A*-manhattan, A*-manhattan_x3.

Uso (desde la carpeta del grupo):
    python code/benchmark.py                    # corrida completa, timeout 30 s
    python code/benchmark.py --rapido           # 1 instancia por nivel, timeout 5 s
    python code/benchmark.py --dominio grid --timeout 60
"""
from __future__ import annotations

import argparse
import sys

from rutas import CODE, RESULTS, preparar_rutas

preparar_rutas()
import dominios                            # noqa: E402
import heuristicas                         # noqa: E402
import motor                               # noqa: E402
from estadistica import escribir_csv, guardar_json, metadata  # noqa: E402

COLUMNAS = ["domain", "level", "instance", "algorithm", "heuristic", "config",
            "status", "cost", "length", "expansions", "max_frontier", "seconds",
            "timeout_s"]


def configuraciones(dominio):
    """[(config, algoritmo, nombre_h, h)]. Salta heurísticas aún sin implementar."""
    out = [("BFS", "bfs", "", None), ("DFS", "dfs", "", None),
           ("UCS", "ucs", "", None), ("IDS", "ids", "", None)]
    for nombre, h in heuristicas.registro()[dominio].items():
        try:
            prob = dominios.problema(dominio, next(dominios.instancias(dominio))[2])
            h(prob, prob.initial)
        except NotImplementedError:
            print(f"  [aviso] {dominio}: heurística '{nombre}' sin implementar, "
                  f"se omite A*-{nombre}", file=sys.stderr)
            continue
        out.append((f"A*-{nombre}", "astar", nombre, h))
    return out


def correr(dominios_a_correr, timeout_s, por_nivel=None):
    filas = []
    for dominio in dominios_a_correr:
        configs = configuraciones(dominio)
        for id_inst, nivel, inst in dominios.instancias(dominio, por_nivel=por_nivel):
            for config, algoritmo, nombre_h, h in configs:
                r = motor.resolver(dominios.problema(dominio, inst), algoritmo,
                                   h=h, timeout_s=timeout_s)
                filas.append({"domain": dominio, "level": nivel,
                              "instance": id_inst, "algorithm": algoritmo,
                              "heuristic": nombre_h, "config": config,
                              **r.fila(), "timeout_s": timeout_s})
                print(f"  {id_inst:<14} {config:<16} {r.status:<11} "
                      f"cost={r.cost!s:<5} exp={r.expansions:>8,} "
                      f"t={r.seconds:7.3f}s", file=sys.stderr)
    return filas


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dominio", choices=dominios.DOMINIOS, action="append")
    ap.add_argument("--timeout", type=float, default=motor.TIMEOUT_S)
    ap.add_argument("--rapido", action="store_true",
                    help="1 instancia por nivel y timeout 5 s (no es la medición oficial)")
    ap.add_argument("--salida", default=None)
    a = ap.parse_args(argv)
    doms = a.dominio or list(dominios.DOMINIOS)
    timeout = 5.0 if a.rapido else a.timeout
    por_nivel = 1 if a.rapido else None
    filas = correr(doms, timeout, por_nivel)
    nombre = a.salida or ("parte1_rapido" if a.rapido else "parte1_mediciones")
    escribir_csv(RESULTS / f"{nombre}.csv", filas, COLUMNAS)
    guardar_json(RESULTS / f"{nombre}_metadata.json",
                 metadata({"timeout_s": timeout, "dominios": doms,
                           "instancias_por_nivel": por_nivel or 10,
                           "filas": len(filas)},
                          archivos=[CODE / f for f in
                                    ("motor.py", "dominios.py", "heuristicas.py",
                                     "benchmark.py")]))
    print(f"{len(filas)} filas -> results/{nombre}.csv", file=sys.stderr)


if __name__ == "__main__":
    main()
