"""Turn results/duel_*.csv into summary tables, figures and paste-ready markdown.

    python analyze.py                       # reads ../results, writes ../fig + ../results/summary.csv
    python analyze.py --results-dir X --fig-dir Y

Optimality rate = share of instances whose answer is optimal_correct (legal,
optimal AND correctly reported cost). `optimal_any_cost` also counts category 3
(optimal path, wrong reported cost) so the report can separate "found the right
path" from "reported it right". Intervals are 95 % Wilson score intervals: with
10 instances per cell they are WIDE, and the figures show that on purpose.
"""
import argparse
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from validator import BADCOST, CATEGORIES, ILLEGAL, NOANSWER, OK, SUBOPT, TIMEOUT

HERE = Path(__file__).resolve().parent.parent
ARMS = ["classical", "llm", "tool", "tool_text"]
ARM_FILES = {"classical": "duel_classical_astar.csv", "llm": "duel_llm.csv", "tool": "duel_tool.csv",
             "tool_text": "duel_tool_text.csv"}   # v1 of the tool arm (optional, shown dashed in grey)
ARM_LABEL = {"classical": "A* clásico", "llm": "LLM solo", "tool": "LLM + herramienta A*",
             "tool_text": "LLM + herramienta (v1, solo texto)"}
DOMAIN_LABEL = {"8puzzle": "8-puzzle (profundidad óptima)", "grid": "Weighted grid (tamaño n×n)"}
# validated categorical slots 1-3 (validate_palette.js --pairs all: PASS, aqua needs labels/markers)
ARM_COLOR = {"classical": "#2a78d6", "llm": "#eb6834", "tool": "#1baf7a", "tool_text": "#8a8985"}
ARM_MARKER = {"classical": "o", "llm": "s", "tool": "^", "tool_text": "x"}
ARM_LINESTYLE = {"tool_text": "--"}
CAT_COLOR = {OK: "#2a78d6", ILLEGAL: "#eb6834", SUBOPT: "#1baf7a", BADCOST: "#eda100",
             NOANSWER: "#e87ba4", TIMEOUT: "#8a8985"}
CAT_LABEL = {OK: "óptimo y costo correcto", ILLEGAL: "1 camino ilegal", SUBOPT: "2 legal pero subóptimo",
             BADCOST: "3 óptimo, costo mal reportado", NOANSWER: "sin respuesta legible", TIMEOUT: "timeout"}
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e3e2dd"


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"),) * 3
    p = k / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, max(0.0, centre - half), min(1.0, centre + half)


def load(results_dir):
    frames = []
    for arm, name in ARM_FILES.items():
        f = results_dir / name
        if f.exists():
            d = pd.read_csv(f)
            d["arm"] = arm
            frames.append(d)
    if not frames:
        raise SystemExit(f"no duel CSVs in {results_dir}; run run_duel.py first")
    return pd.concat(frames, ignore_index=True)


def summarize(df):
    rows = []
    for (arm, domain, level), g in df.groupby(["arm", "domain", "level"]):
        n = len(g)
        counts = g.category.value_counts()
        k_ok, k_any = counts.get(OK, 0), counts.get(OK, 0) + counts.get(BADCOST, 0)
        p, lo, hi = wilson(k_ok, n)
        row = {"arm": arm, "domain": domain, "level": level, "n": n,
               "optimality_rate": p, "ci_low": lo, "ci_high": hi,
               "optimal_any_cost_rate": k_any / n}
        for c in CATEGORIES:
            row[c] = int(counts.get(c, 0))
        rows.append(row)
    return pd.DataFrame(rows)


def style_axes(ax):
    ax.set_facecolor("white")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GRID)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def fig_scaling(summ, out):
    domains = [d for d in ("8puzzle", "grid") if d in set(summ.domain)]
    fig, axes = plt.subplots(1, len(domains), figsize=(5.6 * len(domains), 4.3), sharey=True, squeeze=False)
    for ax, domain in zip(axes[0], domains):
        style_axes(ax)
        levels = sorted(summ[summ.domain == domain].level.unique())
        xs = {lv: i for i, lv in enumerate(levels)}
        arms = [a for a in ARMS if a in set(summ.arm)]
        ends = []
        for j, arm in enumerate(arms):
            s = summ[(summ.arm == arm) & (summ.domain == domain)].sort_values("level")
            x = [xs[lv] + (j - (len(arms) - 1) / 2) * 0.06 for lv in s.level]   # tiny offset so CIs don't overlap
            y = s.optimality_rate.values
            err = [y - s.ci_low.values, s.ci_high.values - y]
            ax.errorbar(x, y, yerr=err, color=ARM_COLOR[arm], marker=ARM_MARKER[arm], markersize=7,
                        linewidth=2, linestyle=ARM_LINESTYLE.get(arm, "-"), capsize=3, elinewidth=1.2,
                        label=ARM_LABEL[arm],
                        markeredgecolor="white", markeredgewidth=1.2)
            if arm != "tool_text":   # the legend names it
                ends.append([y[-1], x[-1], ARM_LABEL[arm]])
        # direct labels at the line ends, nudged apart when two lines end at the same height
        ends.sort(key=lambda e: e[0])
        for i in range(1, len(ends)):
            if ends[i][0] - ends[i - 1][0] < 0.07:
                ends[i][0] = ends[i - 1][0] + 0.07
        for y_lab, x_end, text in ends:
            ax.annotate(text, (x_end, y_lab), xytext=(8, 0), textcoords="offset points",
                        color=INK, fontsize=9, va="center")
        ax.set_xticks(range(len(levels)))
        ax.set_xticklabels([f"{lv}\n(n={int(summ[(summ.domain == domain) & (summ.level == lv)].n.min())})"
                            for lv in levels])
        ax.set_xlim(-0.3, len(levels) - 1 + 0.9)
        ax.set_ylim(-0.03, 1.05)
        ax.set_title(DOMAIN_LABEL[domain], loc="left", color=INK, fontsize=11)
        ax.set_yticks([0, .25, .5, .75, 1])
        ax.set_yticklabels(["0%", "25%", "50%", "75%", "100%"])
    axes[0][0].set_ylabel("Tasa de optimalidad (camino óptimo Y costo correcto)", color=MUTED, fontsize=9)
    fig.text(0.01, 0.005, "Barras: intervalo de Wilson al 95 %. Cada punto es un nivel con sus instancias; no se dice nada de tamaños no probados.",
             color=MUTED, fontsize=8)
    handles, labels = axes[0][0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper right", ncol=min(len(labels), 4), frameon=False, fontsize=9)
    fig.tight_layout(rect=(0, 0.03, 1, 0.94))
    fig.savefig(out, dpi=170, facecolor="white")
    plt.close(fig)


def fig_failures(summ, out):
    arms = [a for a in ("llm", "tool") if a in set(summ.arm)]
    domains = [d for d in ("8puzzle", "grid") if d in set(summ.domain)]
    if not arms:
        return
    fig, axes = plt.subplots(len(arms), len(domains), figsize=(5.6 * len(domains), 3.3 * len(arms)),
                             sharey=True, squeeze=False)
    used = set()
    for r, arm in enumerate(arms):
        for c, domain in enumerate(domains):
            ax = axes[r][c]
            style_axes(ax)
            s = summ[(summ.arm == arm) & (summ.domain == domain)].sort_values("level")
            bottom = [0.0] * len(s)
            for cat in (OK, BADCOST, SUBOPT, ILLEGAL, NOANSWER, TIMEOUT):
                vals = (s[cat] / s.n).values
                if vals.sum() == 0:
                    continue
                used.add(cat)
                ax.bar(range(len(s)), vals, bottom=bottom, color=CAT_COLOR[cat], width=0.62,
                       edgecolor="white", linewidth=2, label=CAT_LABEL[cat])
                bottom = [b + v for b, v in zip(bottom, vals)]
            ax.set_xticks(range(len(s)))
            ax.set_xticklabels([str(lv) for lv in s.level])
            ax.set_ylim(0, 1)
            ax.set_yticks([0, .5, 1])
            ax.set_yticklabels(["0%", "50%", "100%"])
            ax.set_title(f"{ARM_LABEL[arm]} - {DOMAIN_LABEL[domain]}", loc="left", color=INK, fontsize=10)
    handles = [plt.Rectangle((0, 0), 1, 1, color=CAT_COLOR[c]) for c in CATEGORIES if c in used]
    fig.legend(handles, [CAT_LABEL[c] for c in CATEGORIES if c in used], loc="lower center",
               ncol=min(3, len(used)), frameon=False, fontsize=9)
    fig.tight_layout(rect=(0, 0.09, 1, 1))
    fig.savefig(out, dpi=170, facecolor="white")
    plt.close(fig)


STAGES = ["ok", "copy_answer", "bad_args", "no_call", "aborted", "backend"]
STAGE_LABEL = {"ok": "óptimo y costo correcto",
               "copy_answer": "A* respondió bien, pero el modelo copió mal la respuesta",
               "bad_args": "A* rechazó los argumentos que escribió el modelo",
               "no_call": "no llamó a la herramienta",
               "aborted": "se trabó repitiendo texto (Ollama cortó la respuesta)",
               "backend": "error del servidor / timeout"}
# validated in this stacking order (adjacent pairs): blue, aqua, orange, violet; grey = neutral "other"
STAGE_COLOR = {"ok": "#2a78d6", "copy_answer": "#1baf7a", "bad_args": "#eb6834", "no_call": "#4a3aa7",
               "aborted": "#8a8985", "backend": "#c3c2b7"}


def tool_stage(row):
    """At which step did the tool arm fail? (the three things it needs: call, copy in, copy out)"""
    if row.category == OK:
        return "ok"
    detail = str(row.detail) if isinstance(row.detail, str) else ""
    if "repeat limit" in detail or "repeating tokens" in detail:
        return "aborted"
    if row.category == TIMEOUT:
        return "backend"
    if not row.tool_calls or row.tool_calls == 0:
        return "no_call"
    if row.tool_errors and row.tool_errors > 0:
        return "bad_args"
    return "copy_answer"


def fig_tool(df, out):
    t = df[df.arm == "tool"].copy()
    if t.empty:
        return
    t["stage"] = t.apply(tool_stage, axis=1)
    domains = [d for d in ("8puzzle", "grid") if d in set(t.domain)]
    fig, axes = plt.subplots(1, len(domains), figsize=(5.6 * len(domains), 4.0), sharey=True, squeeze=False)
    used = set()
    for ax, domain in zip(axes[0], domains):
        style_axes(ax)
        d = t[t.domain == domain]
        levels = sorted(d.level.unique())
        share = pd.crosstab(d.level, d.stage, normalize="index").reindex(index=levels, columns=STAGES, fill_value=0)
        bottom = [0.0] * len(levels)
        for st in STAGES:
            vals = share[st].values
            if vals.sum() == 0:
                continue
            used.add(st)
            ax.bar(range(len(levels)), vals, bottom=bottom, color=STAGE_COLOR[st], width=0.62,
                   edgecolor="white", linewidth=2)
            bottom = [b + v for b, v in zip(bottom, vals)]
        ax.set_xticks(range(len(levels)))
        ax.set_xticklabels([str(lv) for lv in levels])
        ax.set_ylim(0, 1)
        ax.set_yticks([0, .5, 1])
        ax.set_yticklabels(["0%", "50%", "100%"])
        ax.set_title(DOMAIN_LABEL[domain], loc="left", color=INK, fontsize=10)
    axes[0][0].set_ylabel("% de instancias", color=MUTED, fontsize=9)
    handles = [plt.Rectangle((0, 0), 1, 1, color=STAGE_COLOR[st]) for st in STAGES if st in used]
    fig.legend(handles, [STAGE_LABEL[st] for st in STAGES if st in used], loc="lower center", ncol=2,
               frameon=False, fontsize=8.5)
    fig.tight_layout(rect=(0, 0.17, 1, 1))
    fig.savefig(out, dpi=170, facecolor="white")
    plt.close(fig)


def markdown_tables(df, summ, rdir):
    """Markdown tables ready to paste into REPORT.md (numbers only; the prose is yours)."""
    L = []
    arms = [a for a in ARMS if a in set(summ.arm)]
    for domain in ("8puzzle", "grid"):
        s = summ[summ.domain == domain]
        if s.empty:
            continue
        levels = sorted(s.level.unique())
        L.append(f"**Tasa de optimalidad, {DOMAIN_LABEL[domain]}** (óptimo y costo correcto; IC 95 % de Wilson)\n")
        L.append("| Sistema | " + " | ".join(str(lv) for lv in levels) + " |")
        L.append("|---|" + "---:|" * len(levels))
        for arm in arms:
            cells = []
            for lv in levels:
                r = s[(s.arm == arm) & (s.level == lv)]
                if r.empty:
                    cells.append("–")
                    continue
                r = r.iloc[0]
                k = int(r[OK])
                cells.append(f"{k}/{int(r.n)} ({r.ci_low:.0%}–{r.ci_high:.0%})")
            L.append(f"| {ARM_LABEL[arm]} | " + " | ".join(cells) + " |")
        L.append("")
    L.append("**Resultados por categoría (todas las instancias)**\n")
    L.append("| Sistema | Dominio | n | Óptimo y costo correcto | 1. Ilegal | 2. Legal subóptimo | "
             "3. Óptimo, costo incorrecto | Sin respuesta legible | Timeout |")
    L.append("|---|---|---:|---:|---:|---:|---:|---:|---:|")
    for arm in arms:
        for domain in ("8puzzle", "grid"):
            g = df[(df.arm == arm) & (df.domain == domain)]
            if g.empty:
                continue
            c = g.category.value_counts()
            L.append(f"| {ARM_LABEL[arm]} | {domain} | {len(g)} | " +
                     " | ".join(str(int(c.get(k, 0))) for k in (OK, ILLEGAL, SUBOPT, BADCOST, NOANSWER, TIMEOUT)) + " |")
    L.append("")
    sub = df[df.category == SUBOPT]
    if not sub.empty:
        L.append("Caminos subóptimos que además reportaron mal su costo: " + ", ".join(
            f"{ARM_LABEL[a]} {int((sub[sub.arm == a].cost_reported_ok == False).sum())}/{int((sub.arm == a).sum())}"  # noqa: E712
            for a in arms if (sub.arm == a).any()) + ".\n")
    t = df[df.arm.isin(["tool", "tool_text"])]
    if not t.empty:
        L.append("**Brazo con herramienta**\n")
        L.append("| Versión | Dominio | n | Llamó a A* | Argumentos rechazados | Respondió sin la herramienta | "
                 "Óptimo y costo correcto |")
        L.append("|---|---|---:|---:|---:|---:|---:|")
        for arm in ("tool_text", "tool"):
            for domain in ("8puzzle", "grid"):
                g = t[(t.arm == arm) & (t.domain == domain)]
                if g.empty:
                    continue
                L.append(f"| {ARM_LABEL[arm]} | {domain} | {len(g)} | {int((g.tool_calls > 0).sum())} | "
                         f"{int((g.tool_errors > 0).sum())} | {int(((g.tool_calls == 0) & (g.category != TIMEOUT)).sum())} | "
                         f"{int((g.category == OK).sum())} |")
        L.append("")
    t = df[df.arm == "tool"].copy()
    if not t.empty:
        t["stage"] = t.apply(tool_stage, axis=1)
        L.append("**Dónde falla el brazo con herramienta (v2)**\n")
        L.append("| Dominio | n | " + " | ".join(STAGE_LABEL[st] for st in STAGES) + " |")
        L.append("|---|---:|" + "---:|" * len(STAGES))
        for domain in ("8puzzle", "grid"):
            g = t[t.domain == domain]
            if not g.empty:
                c = g.stage.value_counts()
                L.append(f"| {domain} | {len(g)} | " + " | ".join(str(int(c.get(st, 0))) for st in STAGES) + " |")
        L.append("")
    for rep in sorted(rdir.glob("repro*.csv")):
        r = pd.read_csv(rep)
        n_out = r.answer.fillna("(sin respuesta)").nunique()     # a call with no answer is an outcome too
        n_paths = r.answer.dropna().nunique()
        L.append(f"**Reproducibilidad** (`{rep.name}`): instancia {r.instance_id.iloc[0]}, temperatura "
                 f"{r.temperature.iloc[0]}, {len(r)} llamadas idénticas salvo la semilla → "
                 f"**{n_out} resultado{'s' if n_out != 1 else ''} distinto{'s' if n_out != 1 else ''}** "
                 f"({n_paths} camino{'s' if n_paths != 1 else ''} distinto{'s' if n_paths != 1 else ''}"
                 f"{', más ' + str(int(r.answer.isna().sum())) + ' sin respuesta' if r.answer.isna().any() else ''}).\n")
        L.append("| Llamada | Semilla | Resultado | Costo reportado | Costo real | Óptimo |")
        L.append("|---:|---:|---|---:|---:|---:|")
        for _, x in r.iterrows():
            fmt = lambda v: "–" if pd.isna(v) else str(int(v))  # noqa: E731
            L.append(f"| {x.call} | {x.seed} | {CAT_LABEL.get(x.category, x.category)} | {fmt(x.reported_cost)} | "
                     f"{fmt(x.actual_cost)} | {fmt(x.optimal_cost)} |")
        L.append("")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results-dir", default=str(HERE / "results"))
    ap.add_argument("--fig-dir", default=str(HERE / "fig"))
    a = ap.parse_args()
    rdir, fdir = Path(a.results_dir), Path(a.fig_dir)
    fdir.mkdir(parents=True, exist_ok=True)

    df = load(rdir)
    summ = summarize(df)
    summ.to_csv(rdir / "duel_summary.csv", index=False)
    fig_scaling(summ, fdir / "fig5_scaling_optimality.png")
    fig_failures(summ, fdir / "fig6_failure_breakdown.png")
    fig_tool(df, fdir / "fig7_tool_usage.png")

    show = summ.copy()
    show["optimality"] = show.apply(lambda r: f"{r.optimality_rate:.0%} [{r.ci_low:.0%}-{r.ci_high:.0%}]", axis=1)
    cols = ["arm", "domain", "level", "n", "optimality", "optimal_any_cost_rate"] + [c for c in CATEGORIES if summ[c].sum()]
    print(show[cols].to_string(index=False, float_format=lambda v: f"{v:.2f}"))

    print("\nOverall (all levels pooled):")
    for arm in ARMS:
        g = df[df.arm == arm]
        if g.empty:
            continue
        n = len(g)
        c = g.category.value_counts()
        cost_bad = int(((g.cost_reported_ok == False) & g.category.isin([OK, SUBOPT, BADCOST])).sum())  # noqa: E712
        print(f"  {arm:9s} n={n:3d}  " + "  ".join(f"{k}={int(c.get(k, 0))}" for k in CATEGORIES)
              + f"  | legal paths with a wrong reported cost: {cost_bad}")

    for rep in sorted(rdir.glob("repro*.csv")):
        r = pd.read_csv(rep)
        print(f"\nReproducibility ({r.instance_id.iloc[0]}, T={r.temperature.iloc[0]}): "
              f"{len(r)} calls -> {r.answer.fillna('(no answer)').nunique()} distinct outcomes "
              f"({r.answer.dropna().nunique()} distinct paths); {r.category.value_counts().to_dict()}")
    md = rdir / "duel_tables.md"
    md.write_text(markdown_tables(df, summ, rdir), encoding="utf-8")
    print(f"\nwrote {rdir/'duel_summary.csv'}, {md} and figures in {fdir}")


if __name__ == "__main__":
    main()
