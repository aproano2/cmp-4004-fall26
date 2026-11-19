"""Brazo C: prompt de respuesta directa y lector de la respuesta.

El LLM lee el enunciado y responde él mismo, sin solver.

* `construir_prompt(problema, variante)` arma el texto que recibe el modelo: el
  enunciado y el formato de respuesta (lista exacta de variables y valores). Nunca
  incluye el gold, el modelo_mano ni la verificación manual.
  Probamos tres redacciones solo con los problemas de ejemplo (v1 mínima, v2 con
  instrucciones de formato, v3 que además pide revisar cada pista) y nos quedamos
  con v2, la que mejor respetó el formato.
* `leer_respuesta(texto, problema)` devuelve (respuesta, categoria):
      respuesta  dict {variable: valor}, o None si no se pudo leer nada
      categoria  ""             respuesta bien formada (el gold decide si está bien)
                 "sin_formato"  no hay JSON legible
                 "incompleta"   faltan variables o hay valores fuera de los posibles
  Las dos últimas se detectan sin conocer la respuesta correcta; una respuesta
  bien formada pero equivocada no se puede detectar así (falla en silencio).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from problemas import normalizar, texto_formato  # noqa: E402

CLAVES_PROHIBIDAS = ("gold", "modelo_mano", "verificacion_manual")
_ENVOLTORIOS = ("answer", "respuesta", "solution", "solucion", "solución", "assignment")

_V1 = "{enunciado}\n\n{formato}\n\nAnswer with only a JSON object, no explanation."
_V2 = ("You are solving a logic puzzle. Read all the clues carefully.\n\n{enunciado}\n\n"
       "Required output format:\n{formato}\n"
       'Reply with ONE JSON object that maps every listed variable to its value, e.g. {{"Ana": 1, "Bruno": 2}}.\n\n'
       "Reply with ONLY the JSON, no markdown and no extra text.")
_V3 = _V2 + "\nBefore answering, check silently that your assignment satisfies every numbered clue."
VARIANTES = {"v1": _V1, "v2": _V2, "v3": _V3}
VARIANTE_POR_DEFECTO = "v2"


def extraer_json(texto: str):
    """Primer objeto {...} balanceado del texto. Lanza ValueError si no hay."""
    if not texto:
        raise ValueError("respuesta vacía")
    bloque = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", texto, re.DOTALL)
    candidato = bloque.group(1) if bloque else None
    if candidato is None:
        inicio = texto.find("{")
        if inicio == -1:
            raise ValueError("no hay '{' en la respuesta")
        nivel = 0
        for i in range(inicio, len(texto)):
            if texto[i] == "{":
                nivel += 1
            elif texto[i] == "}":
                nivel -= 1
                if nivel == 0:
                    candidato = texto[inicio:i + 1]
                    break
        if candidato is None:
            raise ValueError("llaves sin cerrar")
    return json.loads(candidato)


def construir_prompt(problema: dict, variante: str | None = None) -> str:
    """Enunciado + formato de respuesta + "responde solo un JSON". Sin gold ni modelo."""
    p = {k: v for k, v in problema.items() if k not in CLAVES_PROHIBIDAS}
    return VARIANTES[variante or VARIANTE_POR_DEFECTO].format(
        enunciado=str(p["enunciado"]).strip(), formato=texto_formato(p).strip())


def leer_respuesta(texto: str, problema: dict) -> tuple[dict | None, str]:
    try:
        datos = extraer_json(texto)
    except (ValueError, json.JSONDecodeError):
        return None, "sin_formato"
    if isinstance(datos, dict) and len(datos) == 1:
        (k, v), = datos.items()
        if str(k).lower() in _ENVOLTORIOS and isinstance(v, dict):
            datos = v
    if not isinstance(datos, dict) or not datos:
        return None, "sin_formato"
    fr = problema["formato_respuesta"]
    dados = {normalizar(k): v for k, v in datos.items()}
    valores = {normalizar(v) for v in fr["valores"]}
    for var in fr["variables"]:
        clave = normalizar(var)
        if clave not in dados or isinstance(dados[clave], (dict, list)) \
                or normalizar(dados[clave]) not in valores:
            return datos, "incompleta"
    return datos, ""
