"""Formato de un problema del dataset y funciones para cargarlo y calificar.

Cada problema es un archivo `problems/<id>.json` con estas claves:

    id                  "facil-01", "medio-07", "dificil-03" (igual al nombre del archivo)
    nivel               "facil" | "medio" | "dificil"
    familia             "einstein" | "horario" | "coloreo" | ... (de dónde viene la idea)
    enunciado           el problema en lenguaje natural (en inglés), SIN la respuesta
    formato_respuesta   {"variables": [...], "valores": [...]}
                        qué hay que responder: la lista exacta de nombres y los
                        valores posibles. Lo ven los brazos B y C (es parte de la
                        pregunta, no de la respuesta).
    modelo_mano         el modelo CSP escrito a mano (brazo A), formato de csp_motor.py
    gold                {variable: valor} para TODAS las variables de formato_respuesta
    verificacion_manual 2-5 frases: cómo comprobamos a mano que el gold cumple todo
    fuente              "inventado" o "adaptado de <dominio clásico>"

Calificar: una respuesta es "correcto" si da exactamente el valor del gold para
cada variable de `formato_respuesta.variables`. Los nombres se comparan sin
mayúsculas, espacios ni tildes ("Ana " == "ana"), y los números aceptan "3" == 3.
"""
from __future__ import annotations

import json
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent          # carpeta del deber
CARPETA_PROBLEMAS = RAIZ / "problems"
NIVELES = ("facil", "medio", "dificil")
CLAVES = ("id", "nivel", "familia", "enunciado", "formato_respuesta",
          "modelo_mano", "gold", "verificacion_manual", "fuente")


def normalizar(x):
    """Clave comparable para nombres y valores."""
    if isinstance(x, bool):
        return str(x).lower()
    if isinstance(x, (int, float)):
        return float(x)
    s = str(x).strip().lower()
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    s = " ".join(s.split())
    try:
        return float(s)
    except ValueError:
        return s


def cargar(carpeta: Path | str | None = None, incluir_ejemplos: bool = False) -> list[dict]:
    """Todos los problemas de `problems/` ordenados por nivel e id.

    Los de `problems/ejemplos/` (formato y few-shot) NO entran en la evaluación
    salvo que se pida `incluir_ejemplos=True`.
    """
    carpeta = Path(carpeta) if carpeta else CARPETA_PROBLEMAS
    archivos = sorted(carpeta.glob("*.json"))
    if incluir_ejemplos:
        archivos += sorted((carpeta / "ejemplos").glob("*.json"))
    problemas = []
    for f in archivos:
        with open(f, encoding="utf-8") as fh:
            p = json.load(fh)
        p["_archivo"] = str(f)
        problemas.append(p)
    orden = {n: i for i, n in enumerate(NIVELES)}
    problemas.sort(key=lambda p: (orden.get(p.get("nivel"), 9), p.get("id", "")))
    return problemas


def ejemplos() -> list[dict]:
    return cargar(CARPETA_PROBLEMAS / "ejemplos")


def calificar(problema: dict, respuesta: dict | None) -> tuple[str, list[str]]:
    """Compara una respuesta {variable: valor} con el gold.

    Devuelve (resultado, detalles) con resultado en
        "correcto" | "incorrecto" | "sin_respuesta"
    `detalles` lista las variables que fallaron o faltaron.
    """
    if not respuesta:
        return "sin_respuesta", ["no hubo respuesta"]
    resp = {normalizar(k): v for k, v in respuesta.items()}
    detalles = []
    for var in problema["formato_respuesta"]["variables"]:
        esperado = problema["gold"][var]
        clave = normalizar(var)
        if clave not in resp:
            detalles.append(f"falta {var}")
        elif normalizar(resp[clave]) != normalizar(esperado):
            detalles.append(f"{var}: dio {resp[clave]!r}, era {esperado!r}")
    faltan = sum(d.startswith("falta") for d in detalles)
    if faltan == len(problema["formato_respuesta"]["variables"]):
        return "sin_respuesta", detalles
    return ("correcto" if not detalles else "incorrecto"), detalles


def texto_formato(problema: dict) -> str:
    """Cómo se le pide la respuesta al LLM (igual para los brazos B y C)."""
    f = problema["formato_respuesta"]
    return ("Variables to report: " + ", ".join(map(str, f["variables"])) + "\n"
            "Possible values: " + ", ".join(map(str, f["valores"])))
