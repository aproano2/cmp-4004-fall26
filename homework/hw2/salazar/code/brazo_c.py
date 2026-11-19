"""Brazo C: el LLM responde directo desde el enunciado.

    python code/brazo_c.py --solo ejemplos     # los 3 problemas de ejemplo
    python code/brazo_c.py                     # dataset x 3 semillas -> results/brazo_c.csv
    python code/brazo_c.py --falso             # sin Ollama (ClienteFalso), solo para probar
    opciones: --variante v1|v2|v3  --semillas 0 1 2

Cada llamada produce una fila con las columnas comunes de resultados.py. El
tiempo del solver es 0 (no hay solver) y siempre es una sola llamada al LLM.
Usamos el mismo cliente, modelo, temperatura y semillas que el brazo B, sin forzar
el modo JSON de Ollama, para que los dos brazos compitan en igualdad.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import config  # noqa: E402
from csp_motor import metricas  # noqa: E402
from llm_cliente import ClienteFalso, ClienteLLM  # noqa: E402
from problemas import calificar, cargar, ejemplos  # noqa: E402
from respuesta_c import VARIANTE_POR_DEFECTO, VARIANTES, construir_prompt, leer_respuesta  # noqa: E402
from resultados import CARPETA, ERRORES_C, a_json, escribir, fila_vacia  # noqa: E402


def correr_problema(p: dict, llm, repeticion: int, semilla: int,
                    variante: str = VARIANTE_POR_DEFECTO) -> dict:
    t0 = time.perf_counter()
    r = llm.llamar(construir_prompt(p, variante), semilla=semilla)
    if r.error:
        respuesta, cat = None, ("no_termina" if r.error == "no_termina" else "sin_formato")
    else:
        respuesta, cat = leer_respuesta(r.texto, p)
    resultado, detalles = calificar(p, respuesta if cat not in ("sin_formato", "no_termina") else None)
    if resultado == "correcto":
        categoria = ""
    else:
        categoria = cat or "incorrecta"
    m = metricas(p["modelo_mano"])
    return fila_vacia(
        problema_id=p["id"], nivel=p["nivel"], n_vars=m["n_vars"],
        n_restricciones=m["n_restricciones"], brazo="C", repeticion=repeticion, semilla=semilla,
        resultado=resultado, categoria_error=categoria,
        detectable=ERRORES_C.get(categoria, ""), iteraciones=1,
        tiempo_total_s=round(time.perf_counter() - t0, 3), tiempo_llm_s=round(r.tiempo_llm_s, 3),
        tiempo_solver_s=0, tokens_entrada=r.tokens_entrada, tokens_salida=r.tokens_salida,
        llamadas_llm=1, cache="si" if r.cache else "no", modelo=llm.modelo, estado_solver="",
        respuesta=a_json(respuesta), detalle="; ".join(detalles[:3]) or (r.error or ""),
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--solo", choices=["ejemplos"], help="correr solo problems/ejemplos/")
    ap.add_argument("--falso", action="store_true", help="usar ClienteFalso (sin Ollama)")
    ap.add_argument("--variante", default=VARIANTE_POR_DEFECTO, choices=sorted(VARIANTES))
    ap.add_argument("--semillas", nargs="*", type=int, default=list(config.SEMILLAS))
    ap.add_argument("--modelo", default=config.MODELO, help="otro modelo de Ollama (experimento de tamaño)")
    args = ap.parse_args()
    problemas = ejemplos() if args.solo == "ejemplos" else cargar()
    llm = ClienteFalso('{"Ana": 1}') if args.falso else ClienteLLM(modelo=args.modelo)
    filas = []
    for p in problemas:
        for rep, semilla in enumerate(args.semillas):
            f = correr_problema(p, llm, rep, semilla, args.variante)
            filas.append(f)
            print(f"{p['id']:<14} s{semilla}  {f['resultado']:<13} {f['categoria_error']:<12} "
                  f"{f['tiempo_llm_s']}s", flush=True)
    nombre = "brazo_c" + ("_ejemplos" if args.solo == "ejemplos" else "") + \
             (f"_{args.variante}" if args.variante != VARIANTE_POR_DEFECTO else "") + \
             (f"_{args.modelo.replace(':', '-')}" if args.modelo != config.MODELO else "") + ".csv"
    ruta = escribir(filas, nombre, CARPETA / "falso" if args.falso else None)
    ok = sum(f["resultado"] == "correcto" for f in filas)
    print(f"Brazo C: {ok}/{len(filas)} correctos -> {ruta}")


if __name__ == "__main__":
    main()
