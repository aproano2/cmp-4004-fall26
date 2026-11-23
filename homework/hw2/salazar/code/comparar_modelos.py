"""Experimento de tamaño: el mismo pipeline con qwen2.5:3b (principal) y qwen2.5:7b.

Lee results/brazo_{b,c}.csv (3B) y results/brazo_{b,c}_qwen2.5-7b.csv (7B) y
escribe results/comparacion_modelos.md y fig/modelos.png.

    python code/comparar_modelos.py
"""
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))

from resultados import CARPETA, RAIZ, leer  # noqa: E402

MODELOS = {"3B": "", "7B": "_qwen2.5-7b"}
BRAZOS = ("B", "Bp", "C")
NOMBRE = {"B": "B", "Bp": "B′", "C": "C"}
NIVELES = ("facil", "medio", "dificil")


def cargar(sufijo):
    filas = []
    for b in ("b", "c"):
        ruta = CARPETA / f"brazo_{b}{sufijo}.csv"
        if ruta.exists():
            filas += leer(ruta.name)
    return filas


def resumen(filas):
    out = {}
    for b in BRAZOS:
        fs = [f for f in filas if f["brazo"] == b]
        if not fs:
            continue
        ok = sum(f["resultado"] == "correcto" for f in fs)
        mal = [f for f in fs if f["resultado"] != "correcto"]
        det = sum(f["detectable"] == "si" for f in mal)
        por_nivel = {n: sum(f["resultado"] == "correcto" for f in fs if f["nivel"] == n) for n in NIVELES}
        out[b] = {"n": len(fs), "ok": ok, "fallos": len(mal), "det": det, "sil": len(mal) - det,
                  "nivel": por_nivel, "cats": Counter(f["categoria_error"] for f in mal)}
    return out


def main() -> None:
    res = {m: resumen(cargar(s)) for m, s in MODELOS.items()}
    lineas = ["# Experimento de tamaño: qwen2.5:3b contra qwen2.5:7b", "",
              "| Modelo | Brazo | Correctas | Fácil / Medio / Difícil | Fallos | Detectables sin gold | Silenciosos |",
              "|---|---|---|---|---|---|---|"]
    for m, r in res.items():
        for b in BRAZOS:
            if b in r:
                d = r[b]
                niv = " / ".join(str(d["nivel"][n]) for n in NIVELES)
                lineas.append(f"| {m} | {NOMBRE[b]} | {d['ok']}/{d['n']} | {niv} (de 21 c/u) | {d['fallos']} | "
                              f"{d['det']} | {d['sil']} |")
    lineas.append("")
    for m, r in res.items():
        if "B" in r:
            lineas.append(f"- Fallos de B con {m}: {dict(r['B']['cats'])}")
        if "Bp" in r:
            lineas.append(f"- Fallos de B′ con {m}: {dict(r['Bp']['cats'])}")
    texto = "\n".join(lineas) + "\n"
    (CARPETA / "comparacion_modelos.md").write_text(texto, encoding="utf-8")
    print(texto)

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 4), dpi=150)
    ancho = 0.35
    for i, (m, r) in enumerate(res.items()):
        bs = [b for b in BRAZOS if b in r]
        xs = [j + (i - 0.5) * ancho for j in range(len(bs))]
        a1.bar(xs, [100 * r[b]["ok"] / r[b]["n"] for b in bs], ancho, label=m,
               color=["#9ecae1", "#3182bd"][i])
        a2.bar(xs, [r[b]["sil"] for b in bs], ancho, label=m, color=["#fcae91", "#cb181d"][i])
    for ax in (a1, a2):
        ax.set_xticks(range(len(BRAZOS)), [NOMBRE[b] for b in BRAZOS])
        ax.grid(axis="y", alpha=0.3)
        ax.legend(fontsize=8)
    a1.set_ylabel("% de instancias correctas")
    a1.set_title("Precisión por tamaño de modelo", fontsize=10)
    a2.set_ylabel("fallos silenciosos (no se detectan sin gold)")
    a2.set_title("Fallos silenciosos por tamaño de modelo", fontsize=10)
    fig.tight_layout()
    fig.savefig(RAIZ / "fig" / "modelos.png")
    plt.close(fig)


if __name__ == "__main__":
    main()
