"""Figuras del duelo 2 (las llama analyze.py; también se puede correr solo)."""
import csv
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt            # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
RES, FIG = ROOT / "results", ROOT / "fig"
COL = {"A": "#1b9e77", "B": "#7570b3", "B'": "#d95f02", "C": "#e7298a"}
NAME = {"A": "A — a mano", "B": "B — híbrido", "B'": "B′ — híbrido + refinamiento",
        "C": "C — directo"}
LEVEL_LABEL = {1: "L1\n4 var", 2: "L2\n8 var", 3: "L3\n10 var", 4: "L4\n15 var"}
CAT_ORDER = ["malformed_syntax", "scope_arity", "over_constrained", "under_constrained",
             "wrong_problem", "timeout"]
CAT_COL = {"malformed_syntax": "#999999", "scope_arity": "#e6ab02", "over_constrained": "#66a61e",
           "under_constrained": "#1f78b4", "wrong_problem": "#e31a1c", "timeout": "#6a3d9a"}
CAT_ES = {"malformed_syntax": "sintaxis mala", "scope_arity": "alcance/aridad",
          "over_constrained": "sobre-restringido", "under_constrained": "sub-restringido",
          "wrong_problem": "problema equivocado", "timeout": "timeout"}


def rd(name):
    return list(csv.DictReader(open(RES / name, encoding="utf-8")))


def fig1_accuracy_vs_difficulty():
    rows = rd("accuracy_by_level.csv")
    fig, ax = plt.subplots(figsize=(9.5, 4.6))
    levels = [1, 2, 3, 4]
    shift = {"A": 0.0, "B": -0.06, "B'": 0.06, "C": 0.0}     # para que B y B′ no se tapen
    for arm in ("A", "B", "B'", "C"):
        main = [next((float(r["accuracy_pct"]) for r in rows if r["arm"] == arm
                      and int(r["level"]) == lv and int(r["rep"]) == 0), None) for lv in levels]
        xs = [lv + shift[arm] for lv in levels]
        ax.plot(xs, main, "o-", color=COL[arm], lw=2.2, label=NAME[arm] + " (T=0)")
        reps = defaultdict(list)
        for r in rows:
            if r["arm"] == arm and int(r["rep"]) > 0:
                reps[int(r["level"])].append(float(r["accuracy_pct"]))
        if reps:
            lo = [min(reps[lv]) for lv in levels]
            hi = [max(reps[lv]) for lv in levels]
            mean = [sum(reps[lv]) / len(reps[lv]) for lv in levels]
            ax.fill_between(xs, lo, hi, color=COL[arm], alpha=0.15)
            ax.plot(xs, mean, "--", color=COL[arm], lw=1, alpha=0.8)
    ax.set_xticks(levels, [LEVEL_LABEL[l] for l in levels])
    ax.set_ylim(-3, 103)
    ax.set_ylabel("problemas resueltos (%)")
    ax.set_xlabel("dificultad (variables del CSP)")
    nrep = len({r["rep"] for r in rows if int(r["rep"]) > 0})
    ax.set_title("Exactitud por brazo y nivel (10 problemas por nivel)\n"
                 f"línea sólida: T=0 · franja: mín–máx de {nrep} réplicas a T=0.7 · trazo: su media",
                 fontsize=10)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8, loc="center left", bbox_to_anchor=(1.01, 0.5))
    fig.tight_layout()
    fig.savefig(FIG / "fig1_accuracy_vs_difficulty.png", dpi=150)
    plt.close(fig)


def fig2_taxonomy():
    ents = [e for e in rd("taxonomy_entries.csv") if e["category"] in CAT_ORDER]
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.3), sharey=True)
    for ax, arm, title in ((axes[0], "B", "B: primer intento"),
                           (axes[1], "B'", "B′: después de ≤3 rondas")):
        bottom = [0] * 4
        for cat in CAT_ORDER:
            vals = [sum(1 for e in ents if e["arm"] == arm and e["category"] == cat
                        and int(e["level"]) == lv) for lv in range(1, 5)]
            det = [sum(1 for e in ents if e["arm"] == arm and e["category"] == cat
                       and int(e["level"]) == lv and e["detectable"] == "True") for lv in range(1, 5)]
            ax.bar(range(1, 5), det, bottom=bottom, color=CAT_COL[cat], label=CAT_ES[cat])
            b2 = [b + d for b, d in zip(bottom, det)]
            ax.bar(range(1, 5), [v - d for v, d in zip(vals, det)], bottom=b2,
                   color=CAT_COL[cat], hatch="///", edgecolor="white")
            bottom = [b + v for b, v in zip(bottom, vals)]
        ax.set_xticks(range(1, 5), [LEVEL_LABEL[l] for l in range(1, 5)])
        ax.set_ylim(0, max(bottom) * 1.12 + 1)
        ax.set_title(title, fontsize=10)
        ax.grid(axis="y", alpha=0.3)
    axes[0].set_ylabel("fallas (todas las corridas, 10 problemas por nivel)")
    handles, labels = axes[0].get_legend_handles_labels()
    from matplotlib.patches import Patch
    handles.append(Patch(facecolor="white", edgecolor="black", hatch="///"))
    labels.append("rayado = silenciosa (no detectable)")
    fig.legend(handles, labels, loc="lower center", ncol=4, fontsize=8, frameon=False)
    fig.suptitle("Taxonomía de fallas del brazo B por nivel", fontsize=11)
    fig.tight_layout(rect=(0, 0.13, 1, 1))
    fig.savefig(FIG / "fig2_taxonomy_by_level.png", dpi=150)
    plt.close(fig)


def fig3_refinement():
    rows = rd("refinement.csv")
    order = ["solved_first_try", "fixed_by_feedback", "feedback_to_wrong_answer",
             "never_converged", "wrong_first_try (no feedback)"]
    lab = {"solved_first_try": "correcto\nal 1er intento", "fixed_by_feedback": "arreglado\ncon feedback",
           "feedback_to_wrong_answer": "feedback →\nsolución mala", "never_converged": "nunca\nconvergió\n(3 rondas)",
           "wrong_first_try (no feedback)": "mal al 1er intento\n(sin feedback:\nel solver respondió)"}
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.4), gridspec_kw={"width_ratios": [1.3, 1]})
    c = Counter(r["kind"] for r in rows)
    axes[0].bar(range(len(order)), [c[k] for k in order],
                color=["#1b9e77", "#d95f02", "#e6ab02", "#999999", "#e31a1c"])
    axes[0].set_xticks(range(len(order)), [lab[k] for k in order], fontsize=7.5)
    axes[0].set_ylabel("instancias (40 problemas × 5 corridas)")
    axes[0].set_title("¿Qué pasó con cada instancia en B′?", fontsize=10)
    for i, k in enumerate(order):
        axes[0].text(i, c[k] + 1, str(c[k]), ha="center", fontsize=9)
    # derecha: de las instancias que recibieron feedback, ¿en qué terminaron?
    fb = [r for r in rows if r["first_stage"] != "solved"]
    firsts = [f for f in ("parse", "schema", "scope", "unsat") if any(r["first_stage"] == f for r in fb)]
    finals = ["solved_ok", "solved_wrong", "still_error"]
    fcol = {"solved_ok": "#1b9e77", "solved_wrong": "#e6ab02", "still_error": "#999999"}
    flab = {"solved_ok": "terminó correcta", "solved_wrong": "terminó con solución equivocada",
            "still_error": "siguió con error tras 3 rondas"}
    bottom = [0] * len(firsts)
    for fin in finals:
        vals = []
        for f in firsts:
            rs = [r for r in fb if r["first_stage"] == f]
            if fin == "solved_ok":
                vals.append(sum(r["kind"] == "fixed_by_feedback" for r in rs))
            elif fin == "solved_wrong":
                vals.append(sum(r["kind"] == "feedback_to_wrong_answer" for r in rs))
            else:
                vals.append(sum(r["kind"] == "never_converged" for r in rs))
        axes[1].bar(firsts, vals, bottom=bottom, color=fcol[fin], label=flab[fin])
        bottom = [b + v for b, v in zip(bottom, vals)]
    axes[1].set_title("Instancias con feedback, según el error del 1er intento", fontsize=10)
    axes[1].set_xlabel("mensaje que recibió el modelo")
    axes[1].legend(fontsize=8)
    for ax in axes:
        ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "fig3_refinement.png", dpi=150)
    plt.close(fig)


def fig4_detectability():
    runs = rd("runs.csv")
    arms = ["B", "B'", "C"]
    det, sil = [], []
    for arm in arms:
        fails = [r for r in runs if r["arm"] == arm and r["outcome"] != "correct"]
        det.append(sum(r["detectable"] == "True" for r in fails))
        sil.append(len(fails) - det[-1])
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    ax.bar(arms, det, color="#1b9e77", label="detectable sin la verdad (falla ruidosa)")
    ax.bar(arms, sil, bottom=det, color="#e31a1c", label="silenciosa (solo se ve con la verdad)")
    for i in range(3):
        tot = det[i] + sil[i]
        if tot:
            ax.text(i, tot + 0.8, f"{100 * det[i] / tot:.0f}% ruidosas", ha="center", fontsize=9)
    ax.set_xticks(range(3), [NAME[a] for a in arms], fontsize=8)
    ax.set_ylabel("fallas (40 problemas × todas las corridas)")
    ax.set_title("¿Las fallas se anuncian solas?", fontsize=11)
    ax.set_ylim(0, max(d + s_ for d, s_ in zip(det, sil)) * 1.35)
    ax.legend(fontsize=8, loc="upper left")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "fig4_detectability.png", dpi=150)
    plt.close(fig)


def fig5_cost():
    """Tokens por intento y por respuesta correcta, sumando las 5 corridas
    (con T=0 sola, C tiene 0 correctas y el costo por correcta es infinito)."""
    runs = rd("runs.csv")
    arms = ["B", "B'", "C"]
    per_att, per_cor, ncor = [], [], []
    for arm in arms:
        rs = [r for r in runs if r["arm"] == arm]
        tok = sum(max(int(r["tokens_in"]), int(r["prompt_chars"]) // 4) + int(r["tokens_out"])
                  for r in rs)
        c = sum(r["outcome"] == "correct" for r in rs)
        per_att.append(tok / len(rs))
        per_cor.append(tok / c if c else float("nan"))
        ncor.append((c, len(rs)))
    fig, ax = plt.subplots(figsize=(7, 4.4))
    x = range(len(arms))
    ax.bar([i - 0.2 for i in x], per_att, 0.4, color="#bbbbbb", label="tokens por intento")
    ax.bar([i + 0.2 for i in x], per_cor, 0.4, color=[COL[a] for a in arms],
           label="tokens por respuesta CORRECTA")
    for i, v in enumerate(per_cor):
        ax.text(i + 0.2, (v if v == v else 0) * 1.02 + 500,
                f"{v:,.0f}\n({ncor[i][0]}/{ncor[i][1]} correctas)" if v == v else "∞", ha="center", fontsize=8)
        ax.text(i - 0.2, per_att[i] + 500, f"{per_att[i]:,.0f}", ha="center", fontsize=8)
    ax.set_xticks(list(x), [NAME[a] for a in arms], fontsize=8)
    ax.set_ylabel("tokens (entrada facturable + salida)")
    ax.set_title("Costo por respuesta correcta (las 5 corridas juntas)", fontsize=11)
    ax.set_ylim(0, max(v for v in per_cor if v == v) * 1.2)
    ax.legend(fontsize=8, loc="upper left")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "fig5_cost_per_correct.png", dpi=150)
    plt.close(fig)


def main():
    FIG.mkdir(exist_ok=True)
    fig1_accuracy_vs_difficulty()
    fig2_taxonomy()
    fig3_refinement()
    fig4_detectability()
    fig5_cost()


if __name__ == "__main__":
    main()
