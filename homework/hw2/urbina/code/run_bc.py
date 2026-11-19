import argparse
import csv
import json
import os
import sys
import time

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE)
sys.path.insert(0, os.path.join(BASE, "code"))

from aicourse.llm import LLM
from csp import backtrack_search
from logic_lm import build_csp, parse_json


def modelo_valido(spec, respuesta):
    variables = spec["variables"]
    if not isinstance(respuesta, dict) or set(respuesta) != set(variables):
        return False

    for nombre in variables:
        if respuesta[nombre] not in variables[nombre]:
            return False

    for c in spec.get("constraints", []):
        if c["type"] == "alldiff":
            usados = []
            for nombre in c["vars"]:
                if respuesta[nombre] in usados:
                    return False
                usados.append(respuesta[nombre])
        elif c["type"] == "eq":
            if respuesta[c["a"]] != c["b"]:
                return False
        elif c["type"] == "neq":
            valor_b = c["b"]
            if isinstance(valor_b, str) and valor_b in variables:
                valor_b = respuesta[valor_b]
            if respuesta[c["a"]] == valor_b:
                return False

    return True


def prompt(arm, puzzle):
    if arm == "B":
        return (
            "Translate the puzzle into a CSP. Output only a JSON object; do not solve it.\n"
            "Each variable is one named person, object, room or cell whose value must be found. "
            "Map each variable name to a flat list of allowed values, with no nested lists. "
            "Do not create variables named 'name', 'value', or 'domain'.\n"
            "Use only these constraints: "
            "{\"type\":\"alldiff\",\"vars\":[\"A\",\"B\"]}, "
            "{\"type\":\"eq\",\"a\":\"A\",\"b\":\"red\"}, "
            "{\"type\":\"neq\",\"a\":\"A\",\"b\":\"B\"}. "
            "For neq, b may also be a domain value. Keep numeric values as numbers.\n"
            "Example: 'Ana and Bo choose different colours, red or blue. Ana chooses red.'\n"
            "{\"variables\":{\"Ana\":[\"red\",\"blue\"],\"Bo\":[\"red\",\"blue\"]},"
            "\"constraints\":[{\"type\":\"alldiff\",\"vars\":[\"Ana\",\"Bo\"]},"
            "{\"type\":\"eq\",\"a\":\"Ana\",\"b\":\"red\"}]}\n"
            "Puzzle:\n" + puzzle
        )

    return (
        "Solve this puzzle directly. Return only one flat JSON object mapping every "
        "named entity or cell to its answer. Do not show your reasoning.\n\nPuzzle:\n" + puzzle
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bank", default=os.path.join(BASE, "problems", "problems_p1.json"))
    parser.add_argument("--output", default=os.path.join(BASE, "results", "bc_results.csv"))
    parser.add_argument("--model", default="qwen2.5:3b")
    parser.add_argument("--ids", nargs="+")
    parser.add_argument("--seed", type=int, default=0)    
    args = parser.parse_args()

    with open(args.bank, encoding="utf-8") as f:
        problemas = json.load(f)["puzzles"]

    if args.ids:
        seleccionados = []
        for problema in problemas:
            if problema["id"] in args.ids:
                seleccionados.append(problema)
        problemas = seleccionados
        
    if not problemas:
        raise ValueError("No hay problemas en el archivo")

    semilla = args.seed
    temperatura = 0.0
    llm = LLM(
        backend="ollama",
        model=args.model,
        cache_dir=os.path.join(BASE, ".llm_cache"),
        seed=semilla,
        temperature=temperatura,
        timeout=300,
    )
    resultados = []

    for problema in problemas:
        for arm in ("B", "C"):
            inicio = time.time()
            salida = llm.complete(prompt(arm, problema["puzzle"]), use_cache=True)
            respuesta = None
            resultado = "no_answer"
            signal = "none"
            error = ""
            tiempo_solver = 0.0

            if salida.error:
                signal = "llm_error"
                error = salida.error

            elif arm == "B":
                #B convierte el texto a CSP y lo manda al solver
                try:
                    spec = parse_json(salida.text)
                    csp = build_csp(spec)
                except Exception as e:
                    signal = "malformed_model"
                    error = str(e)
                else:
                    inicio_solver = time.time()
                    try:
                        respuesta, contador = backtrack_search(
                            csp, use_fc=True, use_mrv=True, limit=200_000
                        )
                    except Exception as e:
                        signal = "solver_error"
                        error = str(e)
                    tiempo_solver = time.time() - inicio_solver

                    if signal == "none":
                        if respuesta == "TIMEOUT":
                            respuesta = None
                            signal = "timeout"
                            error = "call limit exceeded"
                        elif respuesta is None:
                            signal = "unsat"
                            error = "no solution"
                        else:
                            try:
                                es_valido = modelo_valido(spec, respuesta)
                            except Exception as e:
                                es_valido = False
                                error = str(e)

                            if not es_valido:
                                resultado = "incorrect"
                                signal = "invalid_assignment"
                                if not error:
                                    error = "solution violates model"
                            elif respuesta == problema["gold"]:
                                resultado = "correct"
                            else:
                                resultado = "incorrect"

            else:
                #C responde directamente, aqu no se usa el solver.
                try:
                    respuesta = parse_json(salida.text)
                    if not isinstance(respuesta, dict):
                        respuesta = None
                        signal = "malformed_answer"
                        error = "answer is not an object"
                    elif respuesta == problema["gold"]:
                        resultado = "correct"
                    else:
                        resultado = "incorrect"
                except Exception as e:
                    signal = "malformed_answer"
                    error = str(e)

            fila = {
                "id": problema["id"],
                "arm": arm,
                "level": problema["level"],
                "result": resultado,
                "signal": signal,
                "wall_clock_s": round(time.time() - inicio, 6),
                "llm_time_s": round(salida.elapsed, 6),
                "solver_time_s": round(tiempo_solver, 6),
                "tokens_in": salida.meta.get("prompt_eval_count", 0),
                "tokens_out": salida.meta.get("eval_count", 0),
                "model_duration_s": round(salida.meta.get("total_duration", 0) / 1e9, 6),
                "cached": salida.cached,
                "model": salida.model,
                "seed": semilla,
                "temperature": temperatura,
                "answer": json.dumps(respuesta, ensure_ascii=False),
                "error": error,
                "model_output": salida.text,
            }
            resultados.append(fila)
            print(f"{problema['id']} {arm}: {resultado} ({signal})", flush=True)

    #Se conserva la salida original para analizar los errores despues
    carpeta_salida = os.path.dirname(args.output)
    if carpeta_salida:
        os.makedirs(carpeta_salida, exist_ok=True)
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=list(resultados[0]))
        escritor.writeheader()
        escritor.writerows(resultados)


if __name__ == "__main__":
    main()