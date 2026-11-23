"""Figuras del REPORT a partir de los CSV (sin pandas: csv + matplotlib).

    python code/figuras.py                                              # results/ -> fig/
    python code/figuras.py --carpeta results/falso --salida fig/falso   # datos de prueba

Genera:
  precision_vs_dificultad.png  % correcto por nivel, una línea por brazo; la barra es
                               la desviación estándar entre las 3 semillas
  costo_por_correcta.png       tokens y segundos por respuesta correcta, por brazo
  tiempo_llm_vs_solver.png     tiempo medio por instancia: LLM vs solver, por brazo
  iteraciones_bp.png           iteraciones de B' hasta acertar, más "nunca convergió"
  taxonomia_b.png              fallos de B por categoría, según se detecten o no sin gold
  precision_tabla.csv          los números detrás de la primera figura
"""
from __future__ import annotations

import argparse
import csv
import math
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))

from costos import costo_por_correcta  # noqa: E402
from resultados import BRAZOS, RAIZ, TAXONOMIA, leer  # noqa: E402

COLORES = {"A": "#4C72B0", "B": "#DD8452", "Bp": "#55A868", "C": "#C44E52"}
NOMBRES = {"A": "A (a mano)", "B": "B (híbrido)", "Bp": "B′ (con refinamiento)", "C": "C (directo)"}
NIVELES = ("facil", "medio", "dificil")
ETIQ_NIVEL = ["Fácil (≤ 8 var.)", "Medio (9–15)", "Difícil (≥ 16)"]


def _f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return 0.0


def _brazos(filas):
    presentes = {f["brazo"] for f in filas}
    return [b for b in BRAZOS if b in presentes]


def precision(filas):
    """{brazo: {nivel: (media %, desv %, n semillas)}}: precisión por semilla y luego media."""
    acum = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for f in filas:
        acum[f["brazo"]][f["nivel"]][f["repeticion"]].append(f["resultado"] == "correcto")
    res = {}
    for b, por_nivel in acum.items():
        res[b] = {}
        for n, por_rep in por_nivel.items():
            pct = [100 * sum(v) / len(v) for v in por_rep.values()]
            res[b][n] = (statistics.mean(pct), statistics.pstdev(pct) if len(pct) > 1 else 0.0, len(pct))
    return res


def fig_precision(filas, salida):
    res = precision(filas)
    fig, ax = plt.subplots(figsize=(7.5, 4.8), dpi=150)
    for i, b in enumerate(_brazos(filas)):
        xs = [n for n in NIVELES if n in res[b]]
        desplaz = (i - 1.5) * 0.04
        ax.errorbar([NIVELES.index(n) + desplaz for n in xs], [res[b][n][0] for n in xs],
                    yerr=[res[b][n][1] for n in xs], marker="osD^"[i % 4], capsize=4, linewidth=2,
                    color=COLORES[b], label=NOMBRES[b])
    ax.set_xticks(range(3), ETIQ_NIVEL)
    ax.set_ylim(-3, 105)
    ax.set_ylabel("% de instancias correctas")
    ax.set_xlabel("Nivel de dificultad (número de variables del CSP)")
    ax.set_title("Precisión por dificultad (media de 3 semillas; barra = desv. estándar)")
    ax.grid(alpha=0.3)
    ax.legend(loc="center right", fontsize=8)
    fig.tight_layout()
    fig.savefig(salida / "precision_vs_dificultad.png")
    plt.close(fig)
    with open(salida / "precision_tabla.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["brazo", "nivel", "media_pct", "desv_pct", "n_semillas"])
        for b in _brazos(filas):
            for n in NIVELES:
                if n in res[b]:
                    m, s, k = res[b][n]
                    w.writerow([b, n, round(m, 2), round(s, 2), k])


def fig_costo(filas, salida):
    c = costo_por_correcta(filas)
    bs = [b for b in _brazos(filas) if b != "A"]
    tok = [c[b]["tokens_totales"] / c[b]["correctas"] if c[b]["correctas"] else 0 for b in bs]
    seg = [c[b]["segundos_por_correcta"] if not math.isinf(c[b]["segundos_por_correcta"]) else 0 for b in bs]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9, 4), dpi=150)
    for ax, vals, tit in ((a1, tok, "Tokens por respuesta correcta"), (a2, seg, "Segundos por respuesta correcta")):
        barras = ax.bar([NOMBRES[b] for b in bs], vals, color=[COLORES[b] for b in bs])
        for rect, b in zip(barras, bs):
            txt = "sin correctas" if not c[b]["correctas"] else f"{rect.get_height():.0f}"
            ax.annotate(txt, (rect.get_x() + rect.get_width() / 2, rect.get_height()),
                        ha="center", va="bottom", fontsize=8)
        ax.set_title(tit, fontsize=10)
        ax.tick_params(axis="x", labelsize=8, rotation=15)
        ax.grid(axis="y", alpha=0.3)
    fig.suptitle("Costo por respuesta correcta (todo lo gastado ÷ correctas); A no usa LLM", fontsize=10)
    fig.tight_layout()
    fig.savefig(salida / "costo_por_correcta.png")
    plt.close(fig)


def fig_tiempos(filas, salida):
    bs = _brazos(filas)
    llm = [statistics.mean(_f(f["tiempo_llm_s"]) for f in filas if f["brazo"] == b) for b in bs]
    sol = [statistics.mean(_f(f["tiempo_solver_s"]) for f in filas if f["brazo"] == b) for b in bs]
    fig, ax = plt.subplots(figsize=(7, 4.2), dpi=150)
    x = range(len(bs))
    ax.bar(x, llm, color=[COLORES[b] for b in bs], label="LLM")
    ax.bar(x, sol, bottom=llm, color="#333333", label="solver")
    for i, (a, s) in enumerate(zip(llm, sol)):
        ax.annotate(f"LLM {a:.1f} s\nsolver {s * 1000:.1f} ms", (i, a + s), ha="center", va="bottom", fontsize=7)
    ax.set_xticks(list(x), [NOMBRES[b] for b in bs], fontsize=8)
    ax.set_ylabel("segundos por instancia (media)")
    ax.set_title("Dónde se va el tiempo: LLM vs solver")
    ax.legend(fontsize=8)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(salida / "tiempo_llm_vs_solver.png")
    plt.close(fig)


def fig_iteraciones(filas, salida):
    bp = [f for f in filas if f["brazo"] == "Bp"]
    cuenta = Counter(int(_f(f["iteraciones"])) for f in bp if f["resultado"] == "correcto")
    nunca = sum(f["resultado"] != "correcto" for f in bp)
    etiquetas = ["1 (sin refinar)", "2", "3", "4", "nunca"]
    valores = [cuenta.get(1, 0), cuenta.get(2, 0), cuenta.get(3, 0), cuenta.get(4, 0), nunca]
    fig, ax = plt.subplots(figsize=(7, 4), dpi=150)
    barras = ax.bar(etiquetas, valores, color=[COLORES["Bp"]] * 4 + ["#999999"])
    for r in barras:
        ax.annotate(f"{int(r.get_height())}", (r.get_x() + r.get_width() / 2, r.get_height()),
                    ha="center", va="bottom", fontsize=8)
    ax.set_xlabel("intento en el que B′ acertó")
    ax.set_ylabel("instancias")
    ax.set_title(f"Iteraciones hasta acertar en B′ (n = {len(bp)})")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(salida / "iteraciones_bp.png")
    plt.close(fig)


def fig_taxonomia(filas, salida):
    fallos = [f for f in filas if f["brazo"] == "B" and f["resultado"] != "correcto"]
    cuenta = Counter(f["categoria_error"] for f in fallos)
    cats = list(TAXONOMIA)
    vals = [cuenta.get(c, 0) for c in cats]
    colores = ["#55A868" if TAXONOMIA[c] == "si" else "#C44E52" for c in cats]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2), dpi=150, gridspec_kw={"width_ratios": [3, 2]})
    barras = a1.barh(cats, vals, color=colores)
    for r in barras:
        a1.annotate(f"{int(r.get_width())}", (r.get_width(), r.get_y() + r.get_height() / 2),
                    va="center", fontsize=8)
    a1.invert_yaxis()
    a1.set_xlabel("fallos del brazo B (primer intento)")
    a1.set_title("Fallos de B por categoría", fontsize=10)
    a1.grid(axis="x", alpha=0.3)
    # B contra C: ¿cuántos fallos se notan sin la respuesta correcta?
    bs = [b for b in ("B", "Bp", "C") if any(f["brazo"] == b for f in filas)]
    det = [sum(1 for f in filas if f["brazo"] == b and f["resultado"] != "correcto" and f["detectable"] == "si") for b in bs]
    sil = [sum(1 for f in filas if f["brazo"] == b and f["resultado"] != "correcto" and f["detectable"] != "si") for b in bs]
    x = range(len(bs))
    a2.bar(x, det, color="#55A868", label="se detecta sin gold")
    a2.bar(x, sil, bottom=det, color="#C44E52", label="silencioso")
    for i, (d, s_) in enumerate(zip(det, sil)):
        a2.annotate(f"{d} / {s_}", (i, d + s_), ha="center", va="bottom", fontsize=8)
    a2.set_xticks(list(x), [NOMBRES[b] for b in bs], fontsize=8)
    a2.set_ylim(0, max(d + s_ for d, s_ in zip(det, sil)) * 1.15 + 1)
    a2.set_ylabel("fallos")
    a2.set_title("Fallos que se anuncian vs silenciosos", fontsize=10)
    a2.legend(fontsize=8, loc="lower right")
    a2.grid(axis="y", alpha=0.3)
    fig.suptitle("Taxonomía de errores · verde: detectable sin gold · rojo: silencioso", fontsize=10)
    fig.tight_layout()
    fig.savefig(salida / "taxonomia_b.png")
    plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--carpeta", default=None, help="carpeta con los brazo_*.csv (por defecto results/)")
    ap.add_argument("--salida", default=str(RAIZ / "fig"), help="carpeta de salida de los PNG")
    args = ap.parse_args()
    filas = leer(carpeta=args.carpeta)
    salida = Path(args.salida)
    salida.mkdir(parents=True, exist_ok=True)
    fig_precision(filas, salida)
    fig_costo(filas, salida)
    fig_tiempos(filas, salida)
    fig_iteraciones(filas, salida)
    fig_taxonomia(filas, salida)
    print(f"Figuras en {salida}")


if __name__ == "__main__":
    main()
