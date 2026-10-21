"""Utilidades compartidas: CSV, medianas, IQR y huellas (base compartida).

Sin pandas a propósito: en la laptop de Daniel, Windows (Control inteligente de
aplicaciones) bloquea las DLL de pandas. Todo se hace con ``csv`` y ``numpy``.
El enunciado pide medianas e IQR, nunca solo promedios.
"""
from __future__ import annotations

import csv
import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


def escribir_csv(ruta, filas, columnas=None):
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    columnas = columnas or list(filas[0].keys())
    with ruta.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=columnas)
        w.writeheader()
        w.writerows(filas)


def leer_csv(ruta):
    """Lee un CSV como lista de dicts; convierte a número lo que se pueda."""
    def num(v):
        if v in ("", "None"):
            return None
        for tipo in (int, float):
            try:
                return tipo(v)
            except ValueError:
                pass
        return v
    with Path(ruta).open(encoding="utf-8") as f:
        return [{k: num(v) for k, v in fila.items()} for fila in csv.DictReader(f)]


def mediana_iqr(valores):
    """(mediana, q1, q3, n). Ignora None. IQR = q3 - q1."""
    v = np.array([x for x in valores if x is not None], dtype=float)
    if v.size == 0:
        return None, None, None, 0
    q1, med, q3 = np.percentile(v, [25, 50, 75])
    return float(med), float(q1), float(q3), int(v.size)


def agrupar(filas, *claves):
    """{(valor_clave1, valor_clave2, ...): [filas]} conservando el orden."""
    grupos = {}
    for f in filas:
        grupos.setdefault(tuple(f[k] for k in claves), []).append(f)
    return grupos


def sha256(ruta):
    return hashlib.sha256(Path(ruta).read_bytes()).hexdigest()


def metadata(extra=None, archivos=()):
    """Contexto de la corrida + huellas del código usado, para metadata.json."""
    datos = {
        "fecha_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "python": sys.version.split()[0],
        "plataforma": platform.platform(),
        "procesador": platform.processor(),
        "huellas": {Path(a).name: sha256(a) for a in archivos},
    }
    datos.update(extra or {})
    return datos


def guardar_json(ruta, datos):
    Path(ruta).parent.mkdir(parents=True, exist_ok=True)
    Path(ruta).write_text(json.dumps(datos, indent=2, ensure_ascii=False),
                          encoding="utf-8")
