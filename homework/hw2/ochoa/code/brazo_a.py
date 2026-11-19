"""Brazo A: el modelo escrito a mano (modelo_mano) -> nuestro solver.

Es el techo del experimento: si el brazo A no saca 100 %, el problema o el gold
están mal (lo detecta antes verificar_dataset.py). No usa LLM, así que tokens y
tiempo de LLM son 0.

    python code/brazo_a.py          # escribe results/brazo_a.csv
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from csp_motor import ErrorModelo, metricas, resolver  # noqa: E402
from problemas import calificar, cargar  # noqa: E402
from resultados import a_json, escribir, fila_vacia  # noqa: E402


def correr_problema(p: dict, repeticion: int = 0) -> dict:
    t0 = time.perf_counter()
    m = metricas(p["modelo_mano"])
    try:
        r = resolver(p["modelo_mano"], limite_llamadas=2_000_000, limite_segundos=60)
        sol, estado, t_solver = r.solucion, r.estado, r.tiempo_s
    except ErrorModelo as e:
        sol, estado, t_solver = None, f"error:{e.categoria}", 0.0
    resultado, detalles = calificar(p, sol)
    return fila_vacia(
        problema_id=p["id"], nivel=p["nivel"], n_vars=m["n_vars"],
        n_restricciones=m["n_restricciones"], brazo="A", repeticion=repeticion,
        resultado=resultado,
        categoria_error="" if resultado == "correcto" else "modelo_mano",
        detectable="" if resultado == "correcto" else "si",
        iteraciones=0, tiempo_total_s=round(time.perf_counter() - t0, 6),
        tiempo_llm_s=0, tiempo_solver_s=round(t_solver, 6), tokens_entrada=0,
        tokens_salida=0, llamadas_llm=0, cache="", modelo="a_mano",
        estado_solver=estado, respuesta=a_json(sol), detalle="; ".join(detalles[:3]),
    )


def main() -> None:
    problemas = cargar()
    filas = [correr_problema(p, rep) for p in problemas for rep in range(3)]
    ruta = escribir(filas, "brazo_a.csv")
    ok = sum(f["resultado"] == "correcto" for f in filas)
    print(f"Brazo A: {ok}/{len(filas)} correctos -> {ruta}")


if __name__ == "__main__":
    main()
