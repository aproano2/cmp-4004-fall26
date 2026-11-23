"""Brazos B y B': el LLM escribe el modelo CSP y nuestro solver lo resuelve.

B   = un solo intento.
B'  = el mismo primer intento y, si el solver reporta un error que se puede ver
      SIN la respuesta correcta (no parsea, variable inexistente, sin solución,
      varias soluciones, timeout), le devolvemos al modelo SOLO ese mensaje y su
      propio modelo anterior, hasta MAX_REFINAMIENTOS veces.
      Nunca ve el gold ni el modelo_mano: `mensaje_solver` solo recibe el
      resultado del solver y el formato de respuesta (que es parte de la pregunta).

El primer intento de B' es exactamente la misma llamada que B (mismo prompt y
semilla), así que la caché lo reutiliza: B es la iteración 1 de B'.

    python code/brazo_b.py --solo ejemplos     # prueba con los 3 ejemplos
    python code/brazo_b.py                     # dataset x semillas -> results/brazo_b.csv
    python code/brazo_b.py --ids facil-01 medio-02

Además de las filas del CSV, cada intento queda en results/intentos_b.jsonl
(prompt, salida cruda, veredicto del solver) para escribir taxonomy.md.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import config  # noqa: E402
from csp_motor import ErrorModelo, ModeloCSP, metricas, resolver  # noqa: E402
from llm_cliente import ClienteLLM  # noqa: E402
from problemas import calificar, cargar, ejemplos, normalizar, texto_formato  # noqa: E402
from respuesta_c import extraer_json  # noqa: E402
from resultados import CARPETA, TAXONOMIA, a_json, escribir, fila_vacia  # noqa: E402

VOCABULARIO = """Constraint types (use only these):
  {"type": "alldiff", "vars": ["X", "Y", "Z"]}      all different
  {"type": "eq",  "a": "X", "b": "Y"}               X and Y have the same value
  {"type": "eq",  "a": "X", "b": 3}                 X is 3
  {"type": "neq", "a": "X", "b": "Y"}               X and Y differ (b can also be a value)
  {"type": "lt",  "a": "X", "b": "Y"}               X < Y   (numbers only)
  {"type": "gt",  "a": "X", "b": "Y"}               X > Y   (numbers only)
  {"type": "adj", "a": "X", "b": "Y"}               |X - Y| = 1, "next to"
  {"type": "offset", "a": "X", "b": "Y", "k": 1}    X - Y = k, e.g. "X is immediately right of Y\""""


def _ejemplo_fewshot() -> str:
    """El ejemplo fácil, con cada restricción etiquetada con su pista ("clue": 0 = alldiff)."""
    ej = next(p for p in ejemplos() if p["id"] == "ej-facil-01")
    restricciones, pista = [], 0
    for r in ej["modelo_mano"]["constraints"]:
        if r["type"] != "alldiff":
            pista += 1
        restricciones.append({"clue": 0 if r["type"] == "alldiff" else pista, **r})
    modelo = {"variables": ej["modelo_mano"]["variables"], "constraints": restricciones}
    return ("Puzzle:\n" + ej["enunciado"] + "\n" + texto_formato(ej) + "\nJSON:\n"
            + json.dumps(modelo, ensure_ascii=False))


def construir_prompt(problema: dict) -> str:
    """Prompt de traducción. Lleva enunciado + formato, NUNCA el gold ni el modelo_mano."""
    return (
        "Translate the logic puzzle into a constraint satisfaction problem (CSP) in JSON. "
        "Do not solve it. Output only the JSON object.\n\n"
        'Format: {"variables": {"Name": [possible values]}, "constraints": [...]}\n'
        "Use exactly the variable names and possible values listed under the puzzle. "
        "Every listed variable must appear in \"variables\" with all the possible values.\n"
        "Rules: add one alldiff for each group of things that are all different (\"clue\": 0); "
        "then translate EVERY numbered clue, in order, into one constraint whose \"clue\" is the clue number; "
        "use only the names that the clue mentions; write numbers without quotes.\n"
        "\"X is immediately to the right of Y\" is offset a=X, b=Y, k=1; "
        "\"X is immediately to the left of Y\" is offset a=Y, b=X, k=1.\n\n"
        + VOCABULARIO + "\n\nExample.\n" + _ejemplo_fewshot()
        + "\n\nNow this puzzle.\nPuzzle:\n" + problema["enunciado"] + "\n"
        + texto_formato(problema) + "\nJSON:\n"
    )


def _culpables(modelo: dict, maximo: int = 6) -> list[str]:
    """Diagnóstico del solver para un modelo sin solución: las restricciones (no
    alldiff) cuya eliminación individual vuelve el modelo satisfacible. Solo usa
    el modelo del LLM, nunca el gold."""
    restricciones = modelo.get("constraints", [])
    culpables = []
    for i, r in enumerate(restricciones):
        if not isinstance(r, dict) or r.get("type") == "alldiff":
            continue
        prueba = {"variables": modelo["variables"], "constraints": restricciones[:i] + restricciones[i + 1:]}
        try:
            rr = resolver(prueba, max_soluciones=1, limite_llamadas=20_000, limite_segundos=1.0)
        except ErrorModelo:
            continue
        if rr.estado in ("unica", "multiple"):
            culpables.append(json.dumps(r, ensure_ascii=False))
        if len(culpables) >= maximo:
            break
    return culpables


def evaluar_salida(texto: str, problema: dict) -> dict:
    """Pasa la salida del LLM por el parser y el solver. NO usa el gold.

    Devuelve {categoria, mensaje, estado_solver, solucion, tiempo_solver_s}
    con categoria "" (el solver dio una solución única) o una de TAXONOMIA
    excepto "problema_errado", que solo se puede saber con el gold.
    """
    salida = {"categoria": "", "mensaje": "", "estado_solver": "", "solucion": None,
              "tiempo_solver_s": 0.0}
    try:
        modelo = extraer_json(texto)
    except json.JSONDecodeError as e:
        salida.update(categoria="sintaxis",
                      mensaje=f"Your output is not valid JSON: {e.msg} at line {e.lineno}, column {e.colno}.")
        return salida
    except ValueError as e:
        motivo = {"llaves sin cerrar": "the JSON is incomplete: a closing brace '}' is missing at the end",
                  "no hay '{' en la respuesta": "there is no JSON object in your output",
                  "respuesta vacía": "your output is empty"}.get(str(e), str(e))
        salida.update(categoria="sintaxis", mensaje=f"Your output could not be parsed: {motivo}.")
        return salida
    try:
        csp = ModeloCSP(modelo)
    except ErrorModelo as e:
        salida.update(categoria=e.categoria, mensaje=f"The solver rejected the model: {e.mensaje}.")
        return salida
    faltan = [v for v in problema["formato_respuesta"]["variables"]
              if normalizar(v) not in {normalizar(x) for x in csp.variables}]
    if faltan:
        salida.update(categoria="aridad_alcance",
                      mensaje=f"The model is missing the required variables: {', '.join(map(str, faltan))}.")
        return salida
    r = resolver(csp, max_soluciones=2, limite_llamadas=config.LIMITE_LLAMADAS_SOLVER,
                 limite_segundos=config.LIMITE_SEGUNDOS_SOLVER)
    salida.update(estado_solver=r.estado, solucion=r.solucion, tiempo_solver_s=r.tiempo_s)
    if r.estado == "sin_solucion":
        sospechosas = _culpables(modelo)
        extra = (" Removing any ONE of these constraints would make it solvable, so check them against the "
                 "puzzle: " + "; ".join(sospechosas) + ".") if sospechosas else ""
        salida.update(categoria="sobre_restringido",
                      mensaje="The solver proved the model has NO solution: some constraint is wrong or too strong."
                              + extra)
    elif r.estado == "multiple":
        a, b = r.soluciones[:2]
        dif = sorted(k for k in a if a[k] != b[k])
        salida.update(categoria="sub_restringido",
                      mensaje=("The model has MORE THAN ONE solution, so some clue is missing or too weak. "
                               f"Two solutions differ in: {', '.join(dif[:8])}."))
    elif r.estado == "timeout":
        salida.update(categoria="timeout", mensaje="The solver ran out of time on this model.")
    return salida


def prompt_refinamiento(prompt_original: str, salida_anterior: str, mensaje: str) -> str:
    """Solo el mensaje del solver vuelve al modelo (nada de gold)."""
    return (prompt_original + salida_anterior.strip() + "\n\n"
            "Solver feedback: " + mensaje + "\n"
            "Fix the JSON so it is a correct translation of the puzzle. "
            "Output only the corrected JSON object.\nJSON:\n")


def correr_problema(p: dict, llm, repeticion: int, semilla: int, registro: list) -> list[dict]:
    """Devuelve dos filas: la de B (primer intento) y la de Bp (con refinamiento)."""
    m = metricas(p["modelo_mano"])
    base = dict(problema_id=p["id"], nivel=p["nivel"], n_vars=m["n_vars"],
                n_restricciones=m["n_restricciones"], repeticion=repeticion, semilla=semilla,
                modelo=llm.modelo)
    prompt0 = construir_prompt(p)
    prompt = prompt0
    acumulado = {"t_llm": 0.0, "t_sol": 0.0, "tin": 0, "tout": 0, "cache": True}
    filas = []
    t0 = time.perf_counter()
    for it in range(1, config.MAX_REFINAMIENTOS + 2):
        r = llm.llamar(prompt, semilla=semilla)
        if r.error:
            # el LLM no terminó (o falló la llamada): no hay modelo y no hay mensaje del solver
            # que devolver, así que no se refina (mismo criterio que en el HW1)
            cat_err = "no_termina" if r.error == "no_termina" else "sintaxis"
            ev = {"categoria": cat_err, "mensaje": f"LLM: {r.error}", "estado_solver": "",
                  "solucion": None, "tiempo_solver_s": 0.0}
        else:
            ev = evaluar_salida(r.texto, p)
        acumulado["t_llm"] += r.tiempo_llm_s
        acumulado["t_sol"] += ev["tiempo_solver_s"]
        acumulado["tin"] += r.tokens_entrada
        acumulado["tout"] += r.tokens_salida
        acumulado["cache"] &= r.cache
        resultado, detalles = calificar(p, ev["solucion"])
        categoria = ev["categoria"]
        if not categoria and resultado != "correcto":
            categoria = "problema_errado"          # solución única pero de otro problema
        if ev["categoria"] == "sub_restringido" and resultado == "correcto":
            categoria = ""                          # varias soluciones, devolvió la buena por suerte
        registro.append({"problema_id": p["id"], "nivel": p["nivel"], "semilla": semilla,
                         "iteracion": it, "prompt_es_refinamiento": it > 1,
                         "salida": r.texto, "categoria": categoria, "mensaje_solver": ev["mensaje"],
                         "estado_solver": ev["estado_solver"], "resultado": resultado,
                         "detalle": detalles[:6], "tokens_salida": r.tokens_salida,
                         "tiempo_llm_s": round(r.tiempo_llm_s, 3)})
        fila = fila_vacia(
            **base, resultado=resultado if not ev["categoria"] or ev["solucion"] else "sin_respuesta",
            categoria_error=categoria, detectable=TAXONOMIA.get(categoria, ""),
            iteraciones=it, tiempo_total_s=round(time.perf_counter() - t0, 3),
            tiempo_llm_s=round(acumulado["t_llm"], 3), tiempo_solver_s=round(acumulado["t_sol"], 6),
            tokens_entrada=acumulado["tin"], tokens_salida=acumulado["tout"], llamadas_llm=it,
            cache="si" if acumulado["cache"] else "no", estado_solver=ev["estado_solver"],
            respuesta=a_json(ev["solucion"]), detalle="; ".join(detalles[:3]) or ev["mensaje"][:150])
        if it == 1:
            filas.append(dict(fila, brazo="B"))
        # Se refina solo si el solver avisó de algo (sin mirar el gold).
        if not ev["categoria"] or it == config.MAX_REFINAMIENTOS + 1 or r.error:
            filas.append(dict(fila, brazo="Bp"))
            break
        prompt = prompt_refinamiento(prompt0, r.texto, ev["mensaje"])
    return filas


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--solo", choices=["ejemplos"])
    ap.add_argument("--ids", nargs="*", help="correr solo estos problemas")
    ap.add_argument("--semillas", nargs="*", type=int, default=list(config.SEMILLAS))
    ap.add_argument("--modelo", default=config.MODELO, help="otro modelo de Ollama (experimento de tamaño)")
    args = ap.parse_args()
    problemas = ejemplos() if args.solo == "ejemplos" else cargar()
    if args.ids:
        problemas = [p for p in problemas if p["id"] in args.ids]
    llm = ClienteLLM(modelo=args.modelo)
    filas, registro = [], []
    for p in problemas:
        for rep, semilla in enumerate(args.semillas):
            nuevas = correr_problema(p, llm, rep, semilla, registro)
            filas += nuevas
            b, bp = nuevas
            print(f"{p['id']:<14} s{semilla}  B={b['resultado']:<13} {b['categoria_error']:<18}"
                  f" B'={bp['resultado']:<13} it={bp['iteraciones']}  {bp['tiempo_llm_s']}s",
                  flush=True)
    sufijo = "_ejemplos" if args.solo == "ejemplos" else ("_parcial" if args.ids else "")
    if args.modelo != config.MODELO:
        sufijo += "_" + args.modelo.replace(":", "-")
    escribir(filas, f"brazo_b{sufijo}.csv")
    with open(CARPETA / f"intentos_b{sufijo}.jsonl", "w", encoding="utf-8") as fh:
        for r in registro:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    for brazo in ("B", "Bp"):
        sub = [f for f in filas if f["brazo"] == brazo]
        ok = sum(f["resultado"] == "correcto" for f in sub)
        print(f"{brazo}: {ok}/{len(sub)} correctos")


if __name__ == "__main__":
    main()
