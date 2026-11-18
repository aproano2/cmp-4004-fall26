import csv
import json
import os
import time

from arm_a_p1 import V, alldiff, differs, is_, not_
from csp import backtrack_search
from logic_lm import build_csp


def m_q08():
    piezas = ["Aspen", "Bell", "Coin", "Drum"]
    return {
        "variables": V(piezas, [1, 2, 3, 4]),
        "constraints": [
            alldiff(*piezas), is_("Coin", 4),
            *not_("Bell", 1, 3), *not_("Aspen", 2), *not_("Drum", 1)
        ],
    }


def m_q09():
    antenas = ["Birch", "Cedar", "Delta", "Elm"]
    return {
        "variables": V(antenas, ["red", "blue", "green"]),
        "constraints": [
            is_("Birch", "red"), differs("Cedar", "Birch"),
            *not_("Cedar", "green"), differs("Delta", "Cedar"),
            *not_("Delta", "red"), differs("Elm", "Delta"),
            *not_("Elm", "blue")
        ],
    }


def m_q10():
    cursos = ["Alder", "Birch", "Cedar", "Dune", "Elm"]
    return {
        "variables": V(cursos, [1, 2, 3, 4, 5]),
        "constraints": [
            alldiff(*cursos), is_("Elm", 5),
            *not_("Cedar", 1, 2, 4), *not_("Birch", 1, 4),
            *not_("Alder", 4)
        ],
    }


def m_q11():
    sensores = ["A", "B", "C", "D", "E", "F"]
    pares = [
        ("A", "B"), ("A", "C"), ("B", "C"),
        ("D", "A"), ("D", "C"), ("E", "B"),
        ("E", "D"), ("E", "A"), ("F", "C"),
        ("F", "E"), ("F", "B")
    ]
    return {
        "variables": V(sensores, [1, 2, 3]),
        "constraints": [differs(a, b) for a, b in pares]
                       + [is_("A", 1), is_("B", 2)],
    }


def m_q12():
    grupo1 = ["Ava", "Ben", "Cai"]
    grupo2 = ["Dia", "Eli", "Fox"]
    return {
        "variables": V(grupo1 + grupo2, [1, 2, 3]),
        "constraints": [
            alldiff(*grupo1), alldiff(*grupo2), is_("Ava", 1),
            *not_("Ben", 3), differs("Dia", "Ava"),
            *not_("Dia", 2), differs("Eli", "Cai"),
            *not_("Eli", 1), differs("Fox", "Ben")
        ],
    }


def m_q13():
    manana = ["MorningA", "MorningB", "MorningC", "MorningD"]
    tarde = ["AfternoonE", "AfternoonF", "AfternoonG"]
    pares = [
        ("AfternoonE", "MorningA"), ("AfternoonE", "MorningB"),
        ("AfternoonE", "MorningC"), ("AfternoonF", "MorningB"),
        ("AfternoonF", "MorningC"), ("AfternoonF", "MorningD"),
        ("AfternoonG", "MorningA"), ("AfternoonG", "MorningC"),
        ("AfternoonG", "MorningD")
    ]
    return {
        "variables": V(manana + tarde, [1, 2, 3, 4]),
        "constraints": [
            alldiff(*manana), alldiff(*tarde),
            is_("MorningA", 1), is_("MorningB", 2),
            is_("MorningC", 3)
        ] + [differs(a, b) for a, b in pares],
    }


def m_q14():
    celda = lambda fila, columna: f"R{fila}C{columna}"
    celdas = [celda(fila, columna)
              for fila in range(1, 4)
              for columna in range(1, 4)]
    filas = [alldiff(*[celda(fila, columna) for columna in range(1, 4)])
             for fila in range(1, 4)]
    columnas = [alldiff(*[celda(fila, columna) for fila in range(1, 4)])
                for columna in range(1, 4)]
    pistas = [
        is_("R1C1", 1), is_("R1C2", 2),
        is_("R2C1", 2), is_("R2C2", 3)
    ]
    return {
        "variables": V(celdas, [1, 2, 3]),
        "constraints": filas + columnas + pistas,
    }


MODELS = {
    "q08": m_q08, "q09": m_q09, "q10": m_q10,
    "q11": m_q11, "q12": m_q12, "q13": m_q13,
    "q14": m_q14,
}


def run():
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    with open(os.path.join(base, "problems", "problems_p2.json"), encoding="utf-8") as f:
        banco = {p["id"]: p for p in json.load(f)["puzzles"]}

    resultados = []
    for pid, crear_modelo in MODELS.items():
        inicio = time.time()
        csp = build_csp(crear_modelo())
        inicio_solver = time.time()
        respuesta, contador = backtrack_search(csp, use_fc=True, use_mrv=True)
        tiempo_solver = time.time() - inicio_solver

        if respuesta is None or respuesta == "TIMEOUT":
            resultado = "no_answer"
        elif respuesta == banco[pid]["gold"]:
            resultado = "correct"
        else:
            resultado = "incorrect"

        resultados.append({
            "id": pid, "arm": "A", "level": banco[pid]["level"],
            "result": resultado,
            "wall_clock_s": round(time.time() - inicio, 6),
            "llm_time_s": 0.0,
            "solver_time_s": round(tiempo_solver, 6),
            "tokens_in": 0, "tokens_out": 0,
            "solver_calls": contador["calls"],
        })
        print(pid, resultado)

    carpeta_resultados = os.path.join(base, "results")
    os.makedirs(carpeta_resultados, exist_ok=True)
    with open(os.path.join(carpeta_resultados, "arm_a_p2_results.csv"),
              "w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=list(resultados[0]))
        escritor.writeheader()
        escritor.writerows(resultados)


if __name__ == "__main__":
    run()