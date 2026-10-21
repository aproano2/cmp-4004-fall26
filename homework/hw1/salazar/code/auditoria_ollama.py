"""Auditoría de las llamadas que terminaron en error (Daniel).

Una llamada sin texto puede ser dos cosas muy distintas:
  * el MODELO entró en un bucle: generó miles de tokens sin terminar
    (Ollama lo corta con HTTP 500, o pasamos los 300 s)  -> falla del modelo;
  * una falla de INFRAESTRUCTURA: Ollama todavía estaba cancelando la generación
    anterior, o la GPU bajó de velocidad y la llamada se cortó con pocos tokens.

No adivinamos: cruzamos cada error con el log del servidor de Ollama, que
registra cuántos tokens llevaba generados (n_gen) cuando se cortó.

Primera regla (4 de octubre): bucle si n_gen >= 2000 (más de 10 veces la
respuesta normal más larga, 188 tokens); infraestructura en otro caso.

Regla corregida (5 de octubre): repitiendo esas peticiones en streaming
(``diagnostico_500.py``) vimos que un HTTP 500 con tokens generados es Ollama
deteniendo al modelo porque repetía el mismo token ("token repeat limit
reached"), aunque lleve pocos tokens. Entonces:

    bucle del modelo  timeout de 300 s, o HTTP 500 con n_gen > 0
    infraestructura   HTTP 500 con n_gen == 0: la llamada no llegó a generar
                      (Ollama seguía cancelando la anterior) -> se repite Las llamadas de una corrida son secuenciales (un solo
proceso), así que el k-ésimo error del registro corresponde al k-ésimo corte
del log dentro de la ventana de tiempo de esa corrida.

Uso:
    python code/auditoria_ollama.py --system llm --desde "2026/10/04 - 21:35:20" \
        --hasta "2026/10/04 - 23:42:28"
Salidas: results/auditoria_<system>.csv y results/ollama_cortes_<system>.txt
(extracto del log, como evidencia).
"""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

from rutas import RESULTS, preparar_rutas

preparar_rutas()
from estadistica import escribir_csv  # noqa: E402

UMBRAL_TOKENS = 2000
CORTE_INSTANTANEO_S = 5.0
LOG = Path(os.environ.get("LOCALAPPDATA", "")) / "Ollama" / "server.log"
_GIN = re.compile(r"^\[GIN\] (\d{4}/\d\d/\d\d - \d\d:\d\d:\d\d) \| 500 \|\s+(\S+)")
_NGEN = re.compile(r"n_gen =\s+(\d+), tg =\s+([\d.]+) t/s")


def es_bucle(error, ngen):
    """Regla corregida (ver docstring del módulo)."""
    return "timed out" in error.lower() or ngen > 0


def _segundos(texto):
    """'5m0s', '28.3s', '864.3ms' -> segundos."""
    total = 0.0
    for valor, unidad in re.findall(r"([\d.]+)(ms|µs|m|s)", texto):
        total += float(valor) * {"ms": 1e-3, "µs": 1e-6, "m": 60, "s": 1}[unidad]
    return total


def cortes(log, desde, hasta):
    """[(hora, duracion_s, n_gen, tokens_por_s, linea)] de cada HTTP 500 en la ventana."""
    out, ultimo = [], (0, 0.0)
    nueva_tarea = re.compile(r"processing task")
    for linea in Path(log).read_text(encoding="utf-8", errors="replace").splitlines():
        if nueva_tarea.search(linea):
            ultimo = (0, 0.0)
        m = _NGEN.search(linea)
        if m:
            ultimo = (int(m.group(1)), float(m.group(2)))
        g = _GIN.match(linea)
        if g and desde <= g.group(1) <= hasta:
            out.append((g.group(1), _segundos(g.group(2)), ultimo[0], ultimo[1], linea))
    return out


def auditar(system, desde, hasta, log=LOG):
    errores = [json.loads(l) for l in (RESULTS / "llm_calls.jsonl").read_text(
        encoding="utf-8").splitlines() if l.strip()]
    # Solo la corrida principal, que no registraba la hora; las llamadas con hora
    # (reintentos, herramienta) se auditan con --por-hora.
    errores = [e for e in errores if e.get("system") == system and e.get("error")
               and not (e.get("meta") or {}).get("t_fin")]
    cs = cortes(log, desde, hasta)
    if len(cs) != len(errores):
        raise SystemExit(f"{len(errores)} errores en el registro pero {len(cs)} cortes en el "
                         "log: la correspondencia por orden no es segura; revisar a mano.")
    filas = []
    for e, (hora, dur, ngen, tps, _) in zip(errores, cs):
        bucle = es_bucle(e["error"], ngen)
        filas.append({"instance": e["instance"], "round": e.get("round", 0),
                      "error": e["error"], "hora_log": hora, "duracion_s": round(dur, 1),
                      "tokens_generados": ngen, "tokens_por_s": tps,
                      "veredicto": "bucle_del_modelo" if bucle else "infraestructura"})
    escribir_csv(RESULTS / f"auditoria_{system}.csv", filas)
    (RESULTS / f"ollama_cortes_{system}.txt").write_text(
        "\n".join(f"{c[4]}    # n_gen previo = {c[2]}, {c[3]} t/s" for c in cs) + "\n",
        encoding="utf-8")
    return filas


# ---- llamadas con hora registrada (desde el 5 de octubre) ---------------------------

def _hora_log(iso):
    """'2026-10-05T00:52:01' -> '2026/10/05 - 00:52:01' (formato del log de Ollama)."""
    fecha, hora = iso.split("T")
    return fecha.replace("-", "/") + " - " + hora


def _a_segundos(hora_log):
    from datetime import datetime
    return datetime.strptime(hora_log, "%Y/%m/%d - %H:%M:%S").timestamp()


def entradas_con_hora():
    """Errores con t_fin: registro de llamadas (reintentos y herramienta) y
    transcripciones de reproducibilidad."""
    out = []
    for l in (RESULTS / "llm_calls.jsonl").read_text(encoding="utf-8").splitlines():
        e = json.loads(l) if l.strip() else {}
        if e.get("error") and (e.get("meta") or {}).get("t_fin"):
            out.append({"origen": e["system"], "instance": e["instance"],
                        "detalle": f"ronda {e.get('round', 0)}", "error": e["error"],
                        "t_fin": e["meta"]["t_fin"]})
    from rutas import CACHE
    for f in sorted((CACHE / "repro").glob("*.json")):
        e = json.loads(f.read_text(encoding="utf-8"))
        if e.get("error") and (e.get("meta") or {}).get("t_fin"):
            out.append({"origen": "repro", "instance": f.stem, "detalle": e["modo"],
                        "error": e["error"], "t_fin": e["meta"]["t_fin"]})
    return out


def auditar_por_hora(log=LOG, tolerancia_s=5):
    entradas = entradas_con_hora()
    if not entradas:
        return []
    horas = sorted(_hora_log(e["t_fin"]) for e in entradas)
    cs = cortes(log, horas[0][:13] + "00:00", horas[-1])
    filas = []
    for e in entradas:
        t = _a_segundos(_hora_log(e["t_fin"]))
        cerca = [c for c in cs if abs(_a_segundos(c[0]) - t) <= tolerancia_s]
        if not cerca:
            filas.append({**e, "duracion_s": None, "tokens_generados": None,
                          "tokens_por_s": None, "veredicto": "sin_corte_en_log"})
            continue
        hora, dur, ngen, tps, _ = min(cerca, key=lambda c: abs(_a_segundos(c[0]) - t))
        bucle = es_bucle(e["error"], ngen)
        filas.append({**e, "duracion_s": round(dur, 1), "tokens_generados": ngen,
                      "tokens_por_s": tps,
                      "veredicto": "bucle_del_modelo" if bucle else "infraestructura"})
    escribir_csv(RESULTS / "auditoria_por_hora.csv", filas)
    return filas


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--system", default="llm", choices=("llm", "tool"))
    ap.add_argument("--desde", help='"AAAA/MM/DD - HH:MM:SS" (hora del log)')
    ap.add_argument("--hasta")
    ap.add_argument("--por-hora", action="store_true",
                    help="auditar las llamadas con hora registrada (reintentos, repro, herramienta)")
    a = ap.parse_args(argv)
    if a.por_hora:
        filas = auditar_por_hora()
        for f in filas:
            print(f["origen"], f["instance"], f["detalle"], f["tokens_generados"], f["veredicto"])
        return
    filas = auditar(a.system, a.desde, a.hasta)
    infra = sorted({f["instance"] for f in filas if f["veredicto"] == "infraestructura"})
    print(f"{len(filas)} errores: {len(filas) - len(infra)} bucles del modelo, "
          f"{len(infra)} de infraestructura")
    print("volver a correr:", ",".join(infra))


if __name__ == "__main__":
    main()
