"""¿Por qué Ollama responde HTTP 500? Diagnóstico con la API en streaming (Daniel).

El harness del curso pide la respuesta completa (stream=False). Cuando Ollama
corta una generación, devuelve un 500 y el harness descarta el mensaje. Aquí
repetimos la MISMA petición (mismo prompt, temperatura 0, semilla 0) en modo
streaming, que sí entrega el texto parcial y el motivo del corte.

Primer hallazgo (grid-12-07, brazo con herramienta): "prediction aborted, token
repeat limit reached". Es decir, el modelo repetía el mismo token (". . . . .")
y Ollama lo detuvo. Es una falla del modelo, no de la infraestructura.

Este script NO produce resultados del duelo: solo explica los cortes. Las
respuestas oficiales siguen siendo las del harness.

Uso:  python code/diagnostico_500.py llm:grid-12-00 tool:grid-16-01 ...
Salida: results/diagnostico_500.csv
"""
from __future__ import annotations

import json
import sys
import time
import urllib.request

from rutas import RESULTS, preparar_rutas

preparar_rutas()
import dominios  # noqa: E402
import duelo_llm  # noqa: E402
import herramienta  # noqa: E402
from estadistica import escribir_csv  # noqa: E402


def diagnosticar(system, id_inst, timeout=120, max_tokens=3000):
    dominio, _, inst = dominios.buscar(id_inst)
    prompt = (herramienta.prompt_herramienta(dominio, inst) if system == "tool"
              else duelo_llm.prompt_de(dominio, inst))
    body = {"model": duelo_llm.MODELO, "prompt": prompt, "stream": True,
            "options": {"temperature": 0.0, "seed": 0}}
    req = urllib.request.Request("http://localhost:11434/api/generate",
                                 data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    texto, motivo, tokens = "", "", 0
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            for linea in r:
                d = json.loads(linea)
                texto += d.get("response", "")
                tokens += 1 if d.get("response") else 0
                if d.get("error"):
                    motivo = d["error"]
                    break
                if d.get("done"):
                    motivo = f"terminó ({d.get('done_reason')})"
                    break
                # En streaming el timeout de urllib es por lectura, no total: sin
                # este corte, una respuesta en bucle seguiría para siempre.
                if tokens >= max_tokens or time.perf_counter() - t0 > timeout:
                    motivo = f"lo cortamos nosotros: seguía generando ({tokens} tokens)"
                    break
    except Exception as e:                       # noqa: BLE001
        motivo = f"{type(e).__name__}: {e}"
    return {"system": system, "instance": id_inst, "motivo": motivo,
            "tokens_streaming": tokens, "final_del_texto": texto[-80:]}


def main(argv=None):
    pares = [a.split(":") for a in (argv or sys.argv[1:])]
    filas = []
    for system, id_inst in pares:
        f = diagnosticar(system, id_inst)
        print(f"{system:<5} {id_inst:<14} {f['motivo']}  ({f['tokens_streaming']} tokens)",
              flush=True)
        filas.append(f)
        time.sleep(10)                     # que Ollama termine de cancelar
    escribir_csv(RESULTS / "diagnostico_500.csv", filas)


if __name__ == "__main__":
    main()
