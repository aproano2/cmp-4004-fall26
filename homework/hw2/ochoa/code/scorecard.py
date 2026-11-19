"""Duel Scorecard (referencias/duel-scorecard.md) con cuatro columnas: A, B, B', C.

Calcula desde los CSV los ejes que se miden con números y deja en texto los que
son afirmaciones (garantía, interpretabilidad). Escribe results/scorecard.md.

    python code/scorecard.py
    python code/scorecard.py --carpeta results/falso      # prueba con datos falsos
"""
from __future__ import annotations

import argparse
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from resultados import BRAZOS, CARPETA, leer  # noqa: E402

NIVELES = ("facil", "medio", "dificil")
TEXTO = {
    "garantia": {
        "A": "Correcta y única si el modelo a mano es fiel (el solver es completo).",
        "B": "Correcta y única si la traducción es fiel; ninguna sobre la traducción.",
        "Bp": "Igual que B; solo corrige lo que el solver ve.",
        "C": "Ninguna; no hay certificado.",
    },
    "interpretabilidad": {
        "A": "Total: modelo JSON revisable.",
        "B": "Alta: el modelo JSON es un certificado; se ve qué pista falló.",
        "Bp": "Alta, más la traza de mensajes del solver.",
        "C": "Baja: solo una asignación final.",
    },
}


def _f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return 0.0


def _pct(a, b):
    return f"{100 * a / b:.0f} %" if b else "-"


def _p95(v):
    if not v:
        return 0.0
    v = sorted(v)
    return v[min(len(v) - 1, int(round(0.95 * (len(v) - 1))))]


def calcular(filas: list[dict]) -> dict:
    por = defaultdict(list)
    for f in filas:
        por[f["brazo"]].append(f)
    res = {}
    for b in BRAZOS:
        fs = por.get(b, [])
        if not fs:
            continue
        ok = [f for f in fs if f["resultado"] == "correcto"]
        tiempos = [_f(f["tiempo_llm_s"]) + _f(f["tiempo_solver_s"]) for f in fs]
        tokens = sum(_f(f["tokens_entrada"]) + _f(f["tokens_salida"]) for f in fs)
        # reproducibilidad: respuestas distintas entre semillas del mismo problema
        resp = defaultdict(set)
        for f in fs:
            resp[f["problema_id"]].add(f["respuesta"] or f["categoria_error"])
        distintas = statistics.mean(len(s) for s in resp.values()) if resp else 0
        estables = sum(len(s) == 1 for s in resp.values())
        por_nivel = {}
        for n in NIVELES:
            sub = [f for f in fs if f["nivel"] == n]
            por_nivel[n] = _pct(sum(f["resultado"] == "correcto" for f in sub), len(sub))
        fallos = [f for f in fs if f["resultado"] != "correcto"]
        modos = Counter(f["categoria_error"] or "?" for f in fallos)
        det = sum(f["detectable"] == "si" for f in fallos)
        res[b] = {
            "correctas": f"{len(ok)}/{len(fs)} ({_pct(len(ok), len(fs))})",
            "costo": f"{tokens / len(ok):.0f} tokens/correcta" if ok and tokens else ("0 tokens" if not tokens else "inf"),
            "latencia": f"mediana {statistics.median(tiempos):.2f} s · p95 {_p95(tiempos):.2f} s",
            "reproducibilidad": f"{distintas:.2f} respuestas distintas por problema; {estables}/{len(resp)} estables",
            "escalado": " → ".join(f"{n} {por_nivel[n]}" for n in NIVELES),
            "falla": (", ".join(f"{k} {v}" for k, v in modos.most_common(4))
                      + f" · **detectables sin gold: {det}/{len(fallos)}**") if fallos else "sin fallos",
        }
    return res


def tabla(res: dict) -> str:
    cols = [b for b in BRAZOS if b in res]
    nombre = {"A": "A · a mano", "B": "B · híbrido", "Bp": "B′ · refinamiento", "C": "C · directo"}
    filas = [
        ("1 Correctness", lambda b: res[b]["correctas"]),
        ("2 Guarantee", lambda b: TEXTO["garantia"][b]),
        ("3 Cost", lambda b: res[b]["costo"]),
        ("4 Latency", lambda b: res[b]["latencia"]),
        ("5 Reproducibility", lambda b: res[b]["reproducibilidad"]),
        ("6 Scaling", lambda b: res[b]["escalado"]),
        ("7 Interpretability", lambda b: TEXTO["interpretabilidad"][b]),
        ("8 Failure mode", lambda b: res[b]["falla"]),
    ]
    out = ["| Eje | " + " | ".join(nombre[b] for b in cols) + " |",
           "|---|" + "---|" * len(cols)]
    for eje, fn in filas:
        out.append(f"| {eje} | " + " | ".join(fn(b) for b in cols) + " |")
    return "\n".join(out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--carpeta", default=None)
    args = ap.parse_args()
    filas = leer(carpeta=args.carpeta)
    t = tabla(calcular(filas))
    destino = Path(args.carpeta) if args.carpeta else CARPETA
    (destino / "scorecard.md").write_text("# Duel Scorecard\n\n" + t + "\n", encoding="utf-8")
    print(t)


if __name__ == "__main__":
    main()
