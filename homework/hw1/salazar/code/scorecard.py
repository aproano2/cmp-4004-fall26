"""Números del Duel Scorecard, calculados desde results/ (Daniel).

Ninguna cifra del scorecard del REPORT se escribe a mano: todas salen de aquí.
Salida: results/scorecard.csv (una fila por eje y sistema) y la tabla en consola.

Sistemas: clásico = A*-manhattan (Parte 1); llm = brazo puro; tool = brazo con
herramienta. "Correcto" = camino legal, óptimo y con el costo bien reportado
(para A*: costo igual al de UCS).
"""
from __future__ import annotations

import numpy as np

from rutas import RESULTS, preparar_rutas

preparar_rutas()
from estadistica import escribir_csv, leer_csv, mediana_iqr  # noqa: E402


def _p95(v):
    v = [x for x in v if x is not None]
    return float(np.percentile(v, 95)) if v else None


def clasico():
    filas = leer_csv(RESULTS / "parte1_mediciones.csv")
    ucs = {f["instance"]: f["cost"] for f in filas if f["config"] == "UCS"}
    a = [f for f in filas if f["config"] == "A*-manhattan"]
    ok = sum(f["status"] == "solved" and f["cost"] == ucs[f["instance"]] for f in a)
    rep = leer_csv(RESULTS / "reproducibilidad_clasica.csv")
    return {"sistema": "clasico", "n": len(a), "correctas": ok,
            "costo_mediana": mediana_iqr(f["expansions"] for f in a)[0],
            "costo_unidad": "expansiones",
            "latencia_mediana_s": mediana_iqr(f["seconds"] for f in a)[0],
            "latencia_p95_s": _p95([f["seconds"] for f in a]),
            "repro_distintas_de_5": rep[0]["respuestas_distintas"],
            "fallas": f"timeouts={sum(f['status'] == 'timeout' for f in a)}"}


def llm(ruta, nombre):
    if not ruta.exists():
        return None
    f = leer_csv(ruta)
    cats = {}
    for x in f:
        cats[x["category"]] = cats.get(x["category"], 0) + 1
    tokens = [(x["tokens_in"] or 0) + (x["tokens_out"] or 0) for x in f
              if x["tokens_out"] is not None]
    fila = {"sistema": nombre, "n": len(f), "correctas": cats.get("correct", 0),
            "costo_mediana": mediana_iqr(tokens)[0], "costo_unidad": "tokens (entrada+salida)",
            "latencia_mediana_s": mediana_iqr(x["seconds"] for x in f)[0],
            "latencia_p95_s": _p95([x["seconds"] for x in f]),
            "fallas": " ".join(f"{k}={v}" for k, v in sorted(cats.items()))}
    rep = RESULTS / "llm_reproducibilidad_grid-8-00.csv"
    if nombre == "llm" and rep.exists():
        r = [x for x in leer_csv(rep) if x["modo"] == "identicas_t0_s0"]
        fila["repro_distintas_de_5"] = r[0]["respuestas_distintas"]
    return fila


def main():
    filas = [clasico(), llm(RESULTS / "llm_respuestas.csv", "llm"),
             llm(RESULTS / "herramienta_respuestas.csv", "tool")]
    filas = [f for f in filas if f]
    escribir_csv(RESULTS / "scorecard.csv", filas,
                 ["sistema", "n", "correctas", "costo_mediana", "costo_unidad",
                  "latencia_mediana_s", "latencia_p95_s", "repro_distintas_de_5", "fallas"])
    for f in filas:
        print(f)


if __name__ == "__main__":
    main()
