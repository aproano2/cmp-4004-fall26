"""Costo por respuesta CORRECTA, no por intento.

Un brazo barato y equivocado no es barato: sumamos todo lo gastado por un brazo
(todos los intentos, también los fallidos y las iteraciones de B') y lo dividimos
entre sus respuestas correctas. Si un brazo no tiene correctas, su costo por
correcta es infinito.

Nuestro modelo es qwen2.5:3b local (costo de API 0), así que calculamos un
EQUIVALENTE con el precio público de un proveedor hospedado. En la página de
precios de Together AI (consultada el 18-nov-2026) ya no aparece ningún modelo
Qwen2.5; el más cercano en familia y tamaño es Qwen3.5 9B, que es más grande que
el nuestro. Es una aproximación y probablemente sobreestima el costo real.
También reportamos el costo en segundos de cómputo por respuesta correcta.

    python code/costos.py                       # results/ -> results/costos.csv
    python code/costos.py --carpeta results/falso
"""
from __future__ import annotations

import argparse
import csv
import math
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from resultados import BRAZOS, CARPETA, leer  # noqa: E402

# USD por millón de tokens, de la página oficial de precios (serverless inference).
PROVEEDORES = {
    "together": {"modelo": "Qwen3.5 9B", "entrada": 0.17, "salida": 0.25,
                 "fuente": "https://www.together.ai/pricing", "fecha": "2026-11-18"},
}
PRINCIPAL = "together"          # familia Qwen, el tamaño más cercano disponible
PRECIOS = {
    "proveedor": PRINCIPAL,
    "modelo_equivalente": PROVEEDORES[PRINCIPAL]["modelo"],
    "usd_por_millon_entrada": PROVEEDORES[PRINCIPAL]["entrada"],
    "usd_por_millon_salida": PROVEEDORES[PRINCIPAL]["salida"],
    "fuente": PROVEEDORES[PRINCIPAL]["fuente"],
    "fecha_consulta": PROVEEDORES[PRINCIPAL]["fecha"],
}


def _f(x) -> float:
    try:
        return float(x)
    except (TypeError, ValueError):
        return 0.0


def costo_por_correcta(filas: list[dict], proveedor: str = PRINCIPAL) -> dict:
    precio = PROVEEDORES[proveedor]
    acc = defaultdict(lambda: {"intentos": 0, "correctas": 0, "tin": 0.0, "tout": 0.0, "seg": 0.0})
    for f in filas:
        d = acc[f["brazo"]]
        d["intentos"] += 1
        d["correctas"] += f["resultado"] == "correcto"
        d["tin"] += _f(f["tokens_entrada"])
        d["tout"] += _f(f["tokens_salida"])
        d["seg"] += _f(f["tiempo_llm_s"]) + _f(f["tiempo_solver_s"])
    out = {}
    for b, d in acc.items():
        usd = (d["tin"] * precio["entrada"] + d["tout"] * precio["salida"]) / 1_000_000
        ok = d["correctas"]
        out[b] = {"intentos": d["intentos"], "correctas": ok,
                  "tokens_totales": int(d["tin"] + d["tout"]), "usd_total": usd,
                  "usd_por_correcta": usd / ok if ok else math.inf,
                  "segundos_totales": d["seg"],
                  "segundos_por_correcta": d["seg"] / ok if ok else math.inf}
    return out


def _fmt(x, nd=6):
    return "inf" if math.isinf(x) else f"{x:.{nd}f}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--carpeta", default=None)
    args = ap.parse_args()
    filas = leer(carpeta=args.carpeta)
    destino = Path(args.carpeta) if args.carpeta else CARPETA
    lineas = []
    with open(destino / "costos.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["proveedor", "modelo_equivalente", "brazo", "intentos", "correctas", "tokens_totales",
                    "usd_total", "usd_por_correcta", "segundos_totales", "segundos_por_correcta",
                    "fuente", "fecha_consulta"])
        for prov, precio in PROVEEDORES.items():
            c = costo_por_correcta(filas, prov)
            lineas += ["", f"**{prov}** · `{precio['modelo']}` · ${precio['entrada']}/M entrada, "
                           f"${precio['salida']}/M salida · {precio['fuente']} (consultado {precio['fecha']})", "",
                       "| Brazo | Intentos | Correctas | Tokens | USD total | USD por correcta | s por correcta |",
                       "|---|---|---|---|---|---|---|"]
            for b in [x for x in BRAZOS if x in c]:
                d = c[b]
                lineas.append(f"| {b} | {d['intentos']} | {d['correctas']} | {d['tokens_totales']} | "
                              f"{_fmt(d['usd_total'])} | {_fmt(d['usd_por_correcta'])} | "
                              f"{_fmt(d['segundos_por_correcta'], 1)} |")
                w.writerow([prov, precio["modelo"], b, d["intentos"], d["correctas"], d["tokens_totales"],
                            _fmt(d["usd_total"], 8), _fmt(d["usd_por_correcta"], 8),
                            round(d["segundos_totales"], 2), _fmt(d["segundos_por_correcta"], 2),
                            precio["fuente"], precio["fecha"]])
    texto = "\n".join(lineas)
    (destino / "costos.md").write_text("# Costo por respuesta correcta\n" + texto + "\n", encoding="utf-8")
    print(texto)


if __name__ == "__main__":
    main()
