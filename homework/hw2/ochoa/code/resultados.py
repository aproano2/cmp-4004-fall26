"""Formato único de los CSV de resultados (todos los brazos escriben igual).

Una fila = un brazo x un problema x una repetición. Los archivos van en
`results/brazo_a.csv`, `results/brazo_b.csv` (B y B' juntos, columna `brazo`) y
`results/brazo_c.csv`. Las figuras y los costos leen SOLO estas columnas.

Columnas:
    problema_id, nivel, n_vars, n_restricciones
    brazo            A | B | Bp | C        (Bp = B' con auto-refinamiento)
    repeticion       0, 1, 2 ...            (para la varianza)
    semilla          semilla del LLM (vacío en A)
    resultado        correcto | incorrecto | sin_respuesta
    categoria_error  vacío si es correcto; en B/Bp una de TAXONOMIA; en C una de ERRORES_C
    detectable       si | no                ¿se nota el fallo SIN mirar el gold?
    iteraciones      intentos del LLM usados (A=0, B=1, Bp=1..4, C=1)
    tiempo_total_s   reloj de pared de toda la instancia
    tiempo_llm_s     suma del tiempo del LLM (tiempo original aunque venga de caché)
    tiempo_solver_s  suma del tiempo del solver
    tokens_entrada, tokens_salida, llamadas_llm
    cache            si | no                (si TODAS las llamadas vinieron de caché)
    modelo           qwen2.5:3b, ...
    estado_solver    unica | multiple | sin_solucion | timeout | (vacío)
    respuesta        la respuesta final en JSON compacto
    detalle          texto corto: qué falló
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CARPETA = RAIZ / "results"

COLUMNAS = ["problema_id", "nivel", "n_vars", "n_restricciones", "brazo", "repeticion",
            "semilla", "resultado", "categoria_error", "detectable", "iteraciones",
            "tiempo_total_s", "tiempo_llm_s", "tiempo_solver_s", "tokens_entrada",
            "tokens_salida", "llamadas_llm", "cache", "modelo", "estado_solver",
            "respuesta", "detalle"]

BRAZOS = ("A", "B", "Bp", "C")
RESULTADOS = ("correcto", "incorrecto", "sin_respuesta")

# Taxonomía de la consigna para los fallos del brazo B (y B'), con nuestra regla de
# "detectable sin ground truth".
TAXONOMIA = {
    "sintaxis":          "si",   # no parsea / estructura rota: el solver lo rechaza
    "sobre_restringido": "si",   # el solver prueba que no hay solución
    "sub_restringido":   "si",   # el solver encuentra 2+ soluciones (lo contamos)
    "problema_errado":   "no",   # modelo válido y de solución única, pero de otro problema
    "aridad_alcance":    "si",   # variable inexistente / argumentos mal puestos
    "timeout":           "si",   # el solver se queda sin presupuesto
    "no_termina":        "si",   # el LLM no terminó en 300 s (no hay modelo que evaluar)
}
# Errores del brazo C (respuesta directa).
ERRORES_C = {
    "sin_formato":  "si",   # no se pudo leer una respuesta
    "incompleta":   "si",   # faltan variables o hay valores fuera de los posibles
    "incorrecta":   "no",   # respuesta bien formada pero equivocada: falla en silencio
    "no_termina":   "si",   # el LLM no terminó en 300 s
}


def fila_vacia(**valores) -> dict:
    fila = {c: "" for c in COLUMNAS}
    for k, v in valores.items():
        if k not in fila:
            raise KeyError(f"columna desconocida {k!r}")
        fila[k] = v
    return fila


def a_json(x) -> str:
    return "" if x is None else json.dumps(x, ensure_ascii=False, sort_keys=True)


def escribir(filas: list[dict], nombre: str, carpeta: Path | str | None = None) -> Path:
    base = Path(carpeta) if carpeta else CARPETA
    base.mkdir(parents=True, exist_ok=True)
    ruta = base / nombre
    with open(ruta, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNAS)
        w.writeheader()
        for f in filas:
            faltan = set(COLUMNAS) - set(f)
            if faltan:
                raise KeyError(f"faltan columnas {sorted(faltan)}")
            w.writerow({c: f[c] for c in COLUMNAS})
    return ruta


def leer(*nombres: str, carpeta: Path | str | None = None) -> list[dict]:
    """Lee uno o varios CSV (por defecto todos los brazo_*.csv de results/).

    `carpeta` sirve para leer los datos falsos de prueba (results/falso/)."""
    base = Path(carpeta) if carpeta else CARPETA
    # Por defecto solo las corridas oficiales (no las de ejemplos ni las de prueba).
    oficiales = ("brazo_a.csv", "brazo_b.csv", "brazo_c.csv")
    rutas = [base / n for n in nombres] if nombres else [base / n for n in oficiales if (base / n).exists()]
    filas = []
    for r in rutas:
        with open(r, encoding="utf-8") as fh:
            filas.extend(csv.DictReader(fh))
    return filas
