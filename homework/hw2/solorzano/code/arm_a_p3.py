import csv
import json
import os
import time

from csp import backtrack_search
from logic_lm import build_csp

def cargar_modelo(pid):
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    archivo = os.path.join(base, "problems", "problems_p3.json")
    with open(archivo, encoding="utf-8") as f:
        problemas = json.load(f)["puzzles"]
    for problema in problemas:
        if problema["id"] == pid:
            return problema["spec"]
    raise ValueError("No se encontro " + pid)

def m_q15():
    return cargar_modelo("q15")

def m_q16():
    return cargar_modelo("q16")

def m_q17():
    return cargar_modelo("q17")

def m_q18():
    return cargar_modelo("q18")

def m_q19():
    return cargar_modelo("q19")

def m_q20():
    return cargar_modelo("q20")

MODELS = {
    "q15": m_q15, "q16": m_q16, "q17": m_q17,
    "q18": m_q18, "q19": m_q19, "q20": m_q20,
}

def run():
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    archivo_problemas = os.path.join(base, "problems", "problems_p3.json")

    with open(archivo_problemas, encoding="utf-8") as f:
        problemas = json.load(f)["puzzles"]

    resultados = []
    for problema in problemas:
        inicio = time.time()
        csp = build_csp(problema["spec"])
        inicio_solver = time.time()
        respuesta, contador = backtrack_search(csp, use_fc=True, use_mrv=True)
        tiempo_solver = time.time() - inicio_solver

        if respuesta is None or respuesta == "TIMEOUT":
            resultado = "no_answer"
        elif respuesta == problema["gold"]:
            resultado = "correct"
        else:
            resultado = "incorrect"

        resultados.append({
            "id": problema["id"],
            "arm": "A",
            "level": problema["level"],
            "result": resultado,
            "wall_clock_s": round(time.time() - inicio, 6),
            "llm_time_s": 0.0,
            "solver_time_s": round(tiempo_solver, 6),
            "tokens_in": 0,
            "tokens_out": 0,
            "solver_calls": contador["calls"],
        })
        print(problema["id"], resultado)

    archivo_salida = os.path.join(base, "results", "arm_a_p3_results.csv")
    with open(archivo_salida, "w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=list(resultados[0]))
        escritor.writeheader()
        escritor.writerows(resultados)


if __name__ == "__main__":
    run()