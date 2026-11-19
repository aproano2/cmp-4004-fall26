"""Scorecard, detectability table, refinement analysis, cost accounting, figures and taxonomy.md.

usage: python code/analyze.py [--resdir results] [--figdir fig] [--taxonomy-md taxonomy.md]
                              [--price-in USD_per_Mtok --price-out USD_per_Mtok --price-source "Groq, 2026-11-16, model X"]
                              [--usd-per-hour GPU_or_CPU_rate]
Prices are NOT hard-coded on purpose: look up the equivalent hosted model yourself and pass it in.
"""
import argparse, csv, json, math
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, pstdev

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
ARMS = ["A", "B", "B_prime", "C"]
LABEL = {"A": "A — Hand", "B": "B — Hybrid", "B_prime": "B′ — Refinement", "C": "C — Direct"}
COLOR = {"A": "#4c78a8", "B": "#f58518", "B_prime": "#54a24b", "C": "#e45756"}
DIFFS = ["easy", "medium", "hard"]


def T(x): return str(x) == "True"
def f(x): return float(x) if x not in ("", None) else 0.0


def wilson(k, n, z=1.96):
    if n == 0: return (0.0, 0.0)
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def mcnemar_exact(b, c):
    """Two-sided exact test on discordant pairs (b = only first right, c = only second right)."""
    n = b + c
    if n == 0: return 1.0
    k = min(b, c)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)


def load(resdir):
    rows = list(csv.DictReader((resdir / "metrics.csv").open(encoding="utf-8")))
    tax = json.loads((resdir / "taxonomy.json").read_text(encoding="utf-8")) if (resdir / "taxonomy.json").exists() else []
    tr = json.loads((resdir / "bprime_traces.json").read_text(encoding="utf-8")) if (resdir / "bprime_traces.json").exists() else []
    return rows, tax, tr


def write_csv(path, header, rows):
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(header); w.writerows(rows)


def md_table(header, rows):
    out = ["| " + " | ".join(map(str, header)) + " |", "|" + "---|" * len(header)]
    out += ["| " + " | ".join(map(str, r)) + " |" for r in rows]
    return "\n".join(out)


def fmt(x, d=3):
    return f"{x:.{d}f}" if isinstance(x, float) else str(x)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--resdir", default=str(ROOT / "results"))
    ap.add_argument("--figdir", default=str(ROOT / "fig"))
    ap.add_argument("--taxonomy-md", default=str(ROOT / "taxonomy.md"))
    ap.add_argument("--price-in", type=float, help="USD per 1M prompt tokens (equivalent hosted model)")
    ap.add_argument("--price-out", type=float, help="USD per 1M completion tokens")
    ap.add_argument("--price-source", default="", help="where/when the price was read")
    ap.add_argument("--usd-per-hour", type=float, help="optional hardware rate for compute-time costing")
    a = ap.parse_args(argv)
    resdir, figdir = Path(a.resdir), Path(a.figdir); figdir.mkdir(parents=True, exist_ok=True)
    rows, tax, traces = load(resdir)
    g = defaultdict(list)
    for r in rows: g[r["arm"]].append(r)
    arms = [x for x in ARMS if g[x]]
    runs = sorted({r["run"] for r in rows})
    model, temp = rows[0]["model"], rows[0]["temperature"]
    infra = sum(1 for r in rows if r["status"] == "LLM_ERROR")
    if infra: print(f"AVISO: {infra} filas con LLM_ERROR (infraestructura). Reejecuta antes de reportar.")

    # ---------------- scorecard
    sc, det, cost = {}, [], []
    for arm in arms:
        x = g[arm]; n = len(x)
        corr = [r for r in x if T(r["correct"])]
        wrong = [r for r in x if not T(r["correct"])]
        incorrect = [r for r in x if r["outcome"] == "incorrect"]
        noans = [r for r in x if r["outcome"] == "no-answer"]
        ann = [r for r in wrong if T(r["announced_failure"])]
        sil = [r for r in wrong if not T(r["announced_failure"])]
        lo, hi = wilson(len(corr), n)
        per_run = [mean(T(r["correct"]) for r in x if r["run"] == ru) for ru in runs]
        sc[arm] = {"N (problem×run)": n, "correct": len(corr), "incorrect": len(incorrect), "no-answer": len(noans),
                   "accuracy": len(corr) / n, "ci95_lo": lo, "ci95_hi": hi,
                   "std_across_runs": pstdev(per_run) if len(per_run) > 1 else 0.0,
                   "accuracy_when_answered": len(corr) / max(1, len(corr) + len(incorrect)),
                   "wrong_announced": len(ann), "wrong_silent": len(sil),
                   "silent_wrong_rate": len(sil) / n,
                   "mean_wall_s": mean(f(r["wall_time_s"]) for r in x), "mean_llm_s": mean(f(r["llm_time_s"]) for r in x),
                   "mean_solver_s": mean(f(r["solver_time_s"]) for r in x),
                   "mean_prompt_tokens": mean(f(r["prompt_tokens"]) for r in x),
                   "mean_completion_tokens": mean(f(r["completion_tokens"]) for r in x),
                   "mean_attempts": mean(f(r["attempts"]) for r in x)}
        det.append([LABEL[arm], len(wrong), len(ann), len(sil), fmt(len(ann) / len(wrong)) if wrong else "n/a"])
        pt, ct = sum(f(r["prompt_tokens"]) for r in x), sum(f(r["completion_tokens"]) for r in x)
        wall, llm_s = sum(f(r["wall_time_s"]) for r in x), sum(f(r["llm_time_s"]) for r in x)
        k = max(1, len(corr))
        c = {"arm": LABEL[arm], "correct": len(corr), "prompt_tokens": int(pt), "completion_tokens": int(ct),
             "tokens_per_correct": (pt + ct) / k if corr else "inf", "wall_s_per_correct": wall / k if corr else "inf",
             "tokens_per_attempt": (pt + ct) / n}
        if a.price_in is not None and a.price_out is not None:
            usd = (pt * a.price_in + ct * a.price_out) / 1e6
            c.update(total_usd=usd, usd_per_correct=usd / k if corr else "inf", usd_per_attempt=usd / n)
        if a.usd_per_hour is not None:
            c["usd_per_correct_compute_time"] = (wall / 3600 * a.usd_per_hour) / k if corr else "inf"
        cost.append(c)
    metrics = list(next(iter(sc.values())).keys())
    write_csv(resdir / "scorecard.csv", ["metric"] + [LABEL[x] for x in arms],
              [[m] + [round(sc[x][m], 4) if isinstance(sc[x][m], float) else sc[x][m] for x in arms] for m in metrics])
    write_csv(resdir / "detectability.csv", ["arm", "wrong_total", "announced_by_pipeline", "silent", "frac_announced"], det)
    ck = sorted({k for c in cost for k in c}, key=lambda k: (k != "arm", k))
    write_csv(resdir / "cost.csv", ck, [[c.get(k, "") for k in ck] for c in cost])

    # ---------------- by difficulty
    bd = []
    for arm in arms:
        for d in DIFFS:
            s = [r for r in g[arm] if r["difficulty"] == d]
            if s:
                k_ = sum(T(r["correct"]) for r in s); lo, hi = wilson(k_, len(s))
                bd.append([LABEL[arm], d, len(s), k_, round(k_ / len(s), 4), round(lo, 4), round(hi, 4)])
    write_csv(resdir / "by_difficulty.csv", ["arm", "difficulty", "n", "correct", "accuracy", "ci95_lo", "ci95_hi"], bd)

    # ---------------- B vs B' paired test
    paired = {}
    for r in g["B"]: paired[(r["problem_id"], r["run"])] = [T(r["correct"]), None]
    for r in g["B_prime"]:
        if (r["problem_id"], r["run"]) in paired: paired[(r["problem_id"], r["run"])][1] = T(r["correct"])
    pairs = [v for v in paired.values() if v[1] is not None]
    b_only = sum(1 for x, y in pairs if x and not y); bp_only = sum(1 for x, y in pairs if y and not x)
    p_val = mcnemar_exact(b_only, bp_only)

    # ---------------- taxonomy counts (arm B) + right-for-wrong-reasons
    cat = Counter((t["category"], t["detectable_without_ground_truth"]) for t in tax)
    tax_rows = sorted(([c, d, n] for (c, d), n in cat.items()), key=lambda z: -z[2])
    write_csv(resdir / "taxonomy_counts.csv", ["category", "detectable_without_ground_truth", "count"], tax_rows)
    rfwr = [r for r in g["B"] if T(r["correct"]) and r["semantic_class"] not in ("", "equivalent")]

    # ---------------- refinement analysis
    ref_rows, first_fail = [], defaultdict(lambda: Counter())
    n_bp = len(traces)
    at_succ = Counter(t["attempts"] for t in traces if t["correct"])
    never = [t for t in traces if not t["correct"]]
    for i in (1, 2, 3): ref_rows.append(["attempts_to_success", i, at_succ.get(i, 0)])
    ref_rows.append(["never_converged", "", len(never)])
    failed_first = [t for t in traces if t["attempt_classes"] and t["attempt_classes"][0]["category"] != "Correct"]
    fixed_later = [t for t in failed_first if t["correct"]]
    ref_rows += [["attempt1_failed", "", len(failed_first)], ["fixed_in_rounds_2_3", "", len(fixed_later)]]
    for t in failed_first:
        first_fail[t["attempt_classes"][0]["category"]]["fixed" if t["correct"] else "never"] += 1
    for c_, v in first_fail.items():
        ref_rows.append(["first_failure_category:" + c_, "fixed", v["fixed"]]); ref_rows.append(["first_failure_category:" + c_, "never", v["never"]])
    last_cat = Counter(t["attempt_classes"][-1]["category"] for t in never)
    for c_, n_ in last_cat.items(): ref_rows.append(["final_category_of_never_converged", c_, n_])
    stuck = sum(1 for t in never if len({x["category"] for x in t["attempt_classes"]}) == 1)
    ref_rows.append(["never_converged_same_category_every_attempt", "", stuck])
    write_csv(resdir / "refinement.csv", ["section", "key", "value"], ref_rows)

    # ---------------- scorecard.md
    md = [f"Model: `{model}` · temperature {temp} · runs {len(runs)} · N per arm = {len(g[arms[0]])} (problem×run)\n"]
    show = ["N (problem×run)", "correct", "incorrect", "no-answer", "accuracy", "ci95_lo", "ci95_hi", "std_across_runs",
            "accuracy_when_answered", "wrong_announced", "wrong_silent", "silent_wrong_rate", "mean_wall_s", "mean_llm_s",
            "mean_solver_s", "mean_prompt_tokens", "mean_completion_tokens", "mean_attempts"]
    md.append(md_table(["metric"] + [LABEL[x] for x in arms], [[m] + [fmt(sc[x][m]) for x in arms] for m in show]))
    md.append(f"\nB vs B′ (paired): B′ fixes {bp_only} instances, B-only wins {b_only}; exact McNemar p = {p_val:.4f}. "
              f"(B′ attempt 1 is B's call, so B-only wins should be 0.)\n")
    md.append("Detectability of wrong answers\n\n" + md_table(["arm", "wrong", "announced", "silent", "frac announced"], det))
    md.append("\nCost\n\n" + md_table(ck, [[(f"{c[k]:.6g}" if isinstance(c.get(k), float) else c.get(k, "")) for k in ck] for c in cost]))
    if a.price_source: md.append(f"\nPrice source: {a.price_source}")
    (resdir / "scorecard.md").write_text("\n".join(md), encoding="utf-8")

    # ---------------- figures
    plt.figure(figsize=(6.4, 4.2))
    for i, arm in enumerate(arms):
        ys, lo, hi, xs = [], [], [], []
        for j, d in enumerate(DIFFS):
            s = [r for r in g[arm] if r["difficulty"] == d]
            if not s: continue
            k_ = sum(T(r["correct"]) for r in s); l, h = wilson(k_, len(s)); y = k_ / len(s)
            xs.append(j + (i - 1.5) * 0.05); ys.append(y); lo.append(max(0.0, y - l)); hi.append(max(0.0, h - y))
        plt.errorbar(xs, ys, yerr=[lo, hi], marker="o", capsize=3, label=LABEL[arm], color=COLOR[arm])
    n_per = {d: len([r for r in g[arms[0]] if r["difficulty"] == d]) for d in DIFFS}
    plt.xticks(range(3), [f"{d}\n(n={n_per[d]})" for d in DIFFS]); plt.ylim(-0.02, 1.05)
    plt.ylabel("Accuracy (Wilson 95% CI)"); plt.xlabel("Difficulty = # reference CNF clauses band")
    plt.title("Accuracy vs. difficulty"); plt.legend(); plt.grid(alpha=.3); plt.tight_layout()
    plt.savefig(figdir / "accuracy_vs_difficulty.png", dpi=160); plt.close()

    plt.figure(figsize=(6.4, 4.2))
    llm_m = [sc[x]["mean_llm_s"] for x in arms]; sol_m = [sc[x]["mean_solver_s"] for x in arms]
    plt.bar([LABEL[x] for x in arms], llm_m, label="LLM time"); plt.bar([LABEL[x] for x in arms], sol_m, bottom=llm_m, label="Solver time")
    plt.ylabel("Mean seconds per instance"); plt.title("Time breakdown (original measured latency, cache-independent)")
    plt.xticks(rotation=15); plt.legend(); plt.tight_layout(); plt.savefig(figdir / "time_breakdown.png", dpi=160); plt.close()

    plt.figure(figsize=(6.4, 4.2))
    labels_ = ["1", "2", "3", "never"]; vals = [at_succ.get(1, 0), at_succ.get(2, 0), at_succ.get(3, 0), len(never)]
    plt.bar(labels_, vals, color=["#54a24b"] * 3 + ["#e45756"])
    plt.xlabel("Attempt at which B′ first succeeded"); plt.ylabel("Runs"); plt.title(f"Refinement convergence (B′, N={n_bp})")
    plt.tight_layout(); plt.savefig(figdir / "refinement_convergence.png", dpi=160); plt.close()

    plt.figure(figsize=(6.8, 4.2))
    c_ok = [sc[x]["correct"] for x in arms]; c_ann = [sc[x]["wrong_announced"] for x in arms]; c_sil = [sc[x]["wrong_silent"] for x in arms]
    xl = [LABEL[x] for x in arms]
    plt.bar(xl, c_ok, label="correct", color="#54a24b")
    plt.bar(xl, c_ann, bottom=c_ok, label="wrong, ANNOUNCED (parse/UNSAT/timeout/decode/schema)", color="#f2cf5b")
    plt.bar(xl, c_sil, bottom=[o + a_ for o, a_ in zip(c_ok, c_ann)], label="wrong, SILENT", color="#e45756")
    plt.ylabel("Runs"); plt.title("Do the failures announce themselves?"); plt.xticks(rotation=15); plt.legend(fontsize=7)
    plt.tight_layout(); plt.savefig(figdir / "detectability.png", dpi=160); plt.close()

    pids = sorted({r["problem_id"] for r in rows})
    mat = [[mean(T(r["correct"]) for r in g[arm] if r["problem_id"] == p) if any(r["problem_id"] == p for r in g[arm]) else float("nan")
            for arm in arms] for p in pids]
    plt.figure(figsize=(5, 7)); plt.imshow(mat, aspect="auto", vmin=0, vmax=1, cmap="RdYlGn")
    plt.xticks(range(len(arms)), [LABEL[x] for x in arms], rotation=30, ha="right"); plt.yticks(range(len(pids)), pids, fontsize=7)
    plt.colorbar(label="fraction of runs correct"); plt.title("Per-instance success"); plt.tight_layout()
    plt.savefig(figdir / "instance_heatmap.png", dpi=160); plt.close()

    if tax_rows:
        plt.figure(figsize=(8, 0.5 * len(tax_rows) + 1.5))
        names = [r[0][:70] for r in tax_rows]
        cols = ["#54a24b" if r[1].startswith("Yes") else "#e45756" for r in tax_rows]
        plt.barh(names[::-1], [r[2] for r in tax_rows][::-1], color=cols[::-1])
        plt.xlabel("Arm-B failures (green = detectable without ground truth, red = silent)"); plt.title("Arm-B error taxonomy")
        plt.yticks(fontsize=7); plt.tight_layout(); plt.savefig(figdir / "taxonomy_counts.png", dpi=160); plt.close()

    # ---------------- taxonomy.md (auto-generated; discussion belongs in REPORT.md)
    L = ["# Taxonomía de errores — brazo B (AUTO-GENERADO por `code/analyze.py`; no editar a mano)", "",
         f"Modelo: `{model}` · temperatura {temp} · {len(runs)} corridas · {len(g['B'])} intentos de B · {len(tax)} fallos.", "",
         "SAT no tiene cuantificadores; el análogo de los errores de *scope/aridad* de FOL son los errores de **índice/aridad**"
         " (literal fuera de rango, `num_vars` incorrecto, esquema inválido). El ground truth (CNF de referencia) se usa **solo aquí, en el análisis**; "
         "nunca se muestra al modelo ni al bucle de refinamiento.", "",
         "## Conteo por categoría", "", md_table(["categoría", "¿detectable sin ground truth?", "n"], tax_rows or [["(sin fallos)", "", 0]]), ""]
    ann_n = sum(r[2] for r in tax_rows if r[1].startswith("Yes")); L += [
        f"**Fallos de B anunciados por el pipeline: {ann_n} / {len(tax)}** · silenciosos: {len(tax) - ann_n} / {len(tax)}.",
        f"Aciertos de B 'por las razones equivocadas' (respuesta válida con un CNF no equivalente al de referencia): {len(rfwr)} / {sum(T(r['correct']) for r in g['B'])}.", "",
        "## Todos los fallos de B (salida literal del modelo)", ""]
    for i, t in enumerate(tax, 1):
        fence = "````"
        L += [f"### {i}. {t['problem_id']} · run {t['run']} · {t['difficulty']}", "",
              f"- **Categoría:** {t['category']}", f"- **¿Detectable sin ground truth?** {t['detectable_without_ground_truth']}",
              f"- **Estado del solver/validador:** {t['solver_status']}", f"- **Diagnóstico (usa el CNF de referencia):** {t['subcause'] or '—'}",
              "", f"{fence}text", t["model_output"].rstrip(), fence, ""]
    Path(a.taxonomy_md).write_text("\n".join(L), encoding="utf-8")
    print(f"Generado: scorecard.csv/.md, by_difficulty.csv, detectability.csv, cost.csv, refinement.csv, taxonomy_counts.csv, 6-7 figuras y {a.taxonomy_md}")


if __name__ == "__main__":
    main()
