"""Deshace reintentos que la regla corregida de la auditoría no permite (Daniel).

Con la primera regla de ``auditoria_ollama.py`` reintentamos algunas llamadas
que, según la regla corregida, eran bucles del modelo (HTTP 500 con tokens
generados = "token repeat limit reached"). Reintentar una falla del modelo le
daría una segunda oportunidad que los otros sistemas no tienen. Por eso, para
esas instancias, la fila oficial vuelve a ser la del PRIMER intento, que
reconstruimos desde ``results/llm_calls.jsonl`` (el registro guarda cada llamada).

Uso:  python code/restaurar_primer_intento.py
"""
from __future__ import annotations

import json

from rutas import RESULTS, preparar_rutas

preparar_rutas()
import dominios  # noqa: E402
import duelo_llm  # noqa: E402
import herramienta  # noqa: E402
from estadistica import escribir_csv, leer_csv  # noqa: E402

# (system, instance): reintentadas con la primera regla, bucles según la corregida
A_RESTAURAR = {("llm", "grid-8-01"), ("llm", "grid-16-01"), ("llm", "grid-16-02"),
               ("tool", "grid-12-07"), ("tool", "grid-12-09"), ("tool", "grid-16-00"),
               ("tool", "grid-16-01"), ("tool", "grid-16-03"), ("tool", "grid-16-05")}


class _Resp:
    """Lo mínimo de LLMResponse que necesita fila_de()."""
    def __init__(self, e):
        self.error, self.text = e["error"], e.get("text", "")
        self.model, self.temperature, self.seed = e["model"], e["temperature"], e["seed"]
        self.cached, self.elapsed, self.meta = e["cached"], e["elapsed"], e.get("meta") or {}


def primer_error(registro, system, instancia):
    for e in registro:
        if e.get("system") == system and e["instance"] == instancia and e.get("error"):
            return e
    raise SystemExit(f"no hay error registrado para {system}:{instancia}")


def main():
    registro = [json.loads(l) for l in (RESULTS / "llm_calls.jsonl").read_text(
        encoding="utf-8").splitlines() if l.strip()]
    for system, ruta in (("llm", RESULTS / "llm_respuestas.csv"),
                         ("tool", RESULTS / "herramienta_respuestas.csv")):
        filas = leer_csv(ruta)
        for i, f in enumerate(filas):
            if (system, f["instance"]) not in A_RESTAURAR:
                continue
            e = primer_error(registro, system, f["instance"])
            dominio, nivel, inst = dominios.buscar(f["instance"])
            nueva = duelo_llm.fila_de(f["instance"], dominio, nivel, inst, _Resp(e),
                                      e["elapsed"], system=system)
            if system == "tool":
                nueva.update(tool_called=False, tool_json_ok=False, tool_args_match=None,
                             tool_rounds=0, tool_h=f["tool_h"])
            print(f"{system:<5} {f['instance']:<12} {f['category']} -> {nueva['category']}")
            filas[i] = nueva
        cols = duelo_llm.COLUMNAS if system == "llm" else herramienta.COLUMNAS
        escribir_csv(ruta, filas, cols)


if __name__ == "__main__":
    main()
