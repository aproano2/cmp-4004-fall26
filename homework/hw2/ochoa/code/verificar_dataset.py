"""Verificador del dataset. Lo corrimos sobre cada problema antes de usarlo en
los experimentos. Comprueba, problema por problema:

  1. el archivo tiene todas las claves y el id coincide con el nombre del archivo
  2. el modelo_mano se construye sin errores
  3. el solver encuentra UNA sola solución (si hay 0 o 2+, el problema está mal)
  4. esa solución es exactamente el gold, y el gold no viola ninguna restricción
  5. formato_respuesta.variables existen en el gold y los valores del gold están
     en formato_respuesta.valores
  6. el nivel declarado coincide con la métrica (número de variables)
  7. el enunciado no trae la respuesta escrita ("Answer:" / "Solution:")
y al final: ≥ 20 problemas y ≥ 6 por nivel (nuestra meta es 8 por nivel).

Uso (desde la carpeta del deber):
    python code/verificar_dataset.py               # todo problems/
    python code/verificar_dataset.py --ejemplos    # solo problems/ejemplos/
Sale con código 0 si todo está bien y escribe results/dataset_metricas.csv.
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from csp_motor import ErrorModelo, construir, metricas, resolver  # noqa: E402
from problemas import CARPETA_PROBLEMAS, CLAVES, NIVELES, cargar, normalizar  # noqa: E402

# Métrica de dificultad: número de variables del modelo CSP escrito a mano.
UMBRALES = {"facil": (1, 8), "medio": (9, 15), "dificil": (16, 10_000)}
MIN_TOTAL = 20
MIN_POR_NIVEL = 6


def revisar(p: dict) -> tuple[list[str], dict]:
    errores: list[str] = []
    info: dict = {}
    faltan = [c for c in CLAVES if c not in p]
    if faltan:
        return [f"faltan claves: {faltan}"], info
    nombre = Path(p["_archivo"]).stem
    if p["id"] != nombre:
        errores.append(f"id {p['id']!r} distinto del archivo {nombre!r}.json")
    if p["nivel"] not in NIVELES:
        errores.append(f"nivel {p['nivel']!r} no es facil/medio/dificil")
    texto = p["enunciado"].lower()
    if "answer:" in texto or "solution:" in texto:
        errores.append("el enunciado parece traer la respuesta")
    try:
        csp = construir(p["modelo_mano"])
    except ErrorModelo as e:
        return errores + [f"modelo_mano no se construye ({e.categoria}): {e.mensaje}"], info
    info = metricas(p["modelo_mano"])
    r = resolver(csp, max_soluciones=2, limite_llamadas=2_000_000, limite_segundos=60)
    info.update(estado=r.estado, llamadas=r.llamadas, tiempo_solver_s=round(r.tiempo_s, 4))
    if r.estado != "unica":
        errores.append(f"el modelo_mano tiene estado {r.estado!r}: debe tener solución única")
        if r.estado == "multiple":
            a, b = r.soluciones[:2]
            dif = {k: (a[k], b[k]) for k in a if a[k] != b[k]}
            errores.append(f"  dos soluciones distintas en: {dif}")
    gold = p["gold"]
    fr = p["formato_respuesta"]
    valores = {normalizar(v) for v in fr.get("valores", [])}
    for var in fr.get("variables", []):
        if var not in gold:
            errores.append(f"formato_respuesta pide {var!r} pero no está en el gold")
        elif normalizar(gold[var]) not in valores:
            errores.append(f"gold[{var!r}]={gold[var]!r} no está en formato_respuesta.valores")
    viol = csp.violaciones({k: v for k, v in gold.items() if k in csp.variables})
    viol = [v for v in viol if not v.startswith("falta")]
    if viol:
        errores.append(f"el gold incumple restricciones del modelo_mano: {viol[:5]}")
    if r.estado == "unica":
        dif = [k for k in gold if k in r.solucion and normalizar(r.solucion[k]) != normalizar(gold[k])]
        if dif:
            errores.append(f"el solver da otra respuesta que el gold en {dif}")
    lo, hi = UMBRALES.get(p["nivel"], (0, 0))
    if not lo <= info["n_vars"] <= hi:
        errores.append(f"nivel {p['nivel']} pide {lo}-{hi} variables y el modelo tiene {info['n_vars']}")
    return errores, info


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ejemplos", action="store_true", help="revisar solo problems/ejemplos/")
    args = ap.parse_args()
    carpeta = CARPETA_PROBLEMAS / "ejemplos" if args.ejemplos else CARPETA_PROBLEMAS
    problemas = cargar(carpeta)
    if not problemas:
        print(f"No hay problemas en {carpeta}")
        return 1
    total_errores = 0
    filas = []
    print(f"{'id':<14}{'nivel':<9}{'vars':>5}{'restr':>6}{'llamadas':>10}  estado")
    for p in problemas:
        errores, info = revisar(p)
        estado = "OK" if not errores else "ERROR"
        print(f"{p.get('id', '?'):<14}{p.get('nivel', '?'):<9}{info.get('n_vars', '-'):>5}"
              f"{info.get('n_restricciones', '-'):>6}{info.get('llamadas', '-'):>10}  {estado}")
        for e in errores:
            print(f"    - {e}")
        total_errores += len(errores)
        filas.append({"problema_id": p.get("id"), "nivel": p.get("nivel"),
                      "familia": p.get("familia"), **info, "ok": not errores})
    conteo = {n: sum(p.get("nivel") == n for p in problemas) for n in NIVELES}
    print(f"\nTotal: {len(problemas)} problemas  {conteo}")
    if not args.ejemplos:
        if len(problemas) < MIN_TOTAL:
            print(f"  - faltan problemas: la consigna pide al menos {MIN_TOTAL}")
            total_errores += 1
        for n, c in conteo.items():
            if c < MIN_POR_NIVEL:
                print(f"  - el nivel {n} tiene {c}; necesitamos al menos {MIN_POR_NIVEL}")
                total_errores += 1
        salida = CARPETA_PROBLEMAS.parent / "results" / "dataset_metricas.csv"
        salida.parent.mkdir(exist_ok=True)
        campos = sorted({k for f in filas for k in f}, key=lambda k: (k != "problema_id", k))
        with open(salida, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=campos)
            w.writeheader()
            w.writerows(filas)
        print(f"Métricas guardadas en {salida.relative_to(CARPETA_PROBLEMAS.parent)}")
    if total_errores:
        print(f"\nHAY {total_errores} ERRORES en el dataset.")
        return 1
    print("\nTODO EL DATASET ESTÁ BIEN.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
