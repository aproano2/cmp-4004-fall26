"""Joint evaluation of arms A, B, B', C: scorecard, difficulty table, variance, figures.

    python code/evaluation.py

Reads results/arm_a.csv, arm_b.csv, arm_b_refined.csv, arm_c.csv (main protocol:
temperature 0, seed 0) and, if present, results/variance/*.jsonl (temperature 0.7,
other seeds; only arm C was replicated). Writes results/scorecard.csv, results/accuracy_by_difficulty.csv,
results/variance_summary.csv, results/c_failure_analysis.csv and three figures in fig/.
B/B' CSVs are only read, never modified.
Never calls an LLM. Ground truth is used only here, for grading and post-hoc analysis.

Cost: local model priced at the equivalent hosted rate given by --input-price /
--output-price (USD per 1M tokens). Default: Together AI "Qwen2.5 7B Instruct
Turbo", 0.30 / 0.30, together.ai/pricing consulted 2026-11-17 (smallest hosted
Qwen2.5 listed; an upper bound for a 3B model).
"""
from __future__ import annotations

import argparse
import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from csp_spec import check_assignment  # noqa: E402
from results_schema import grade  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
RES, FIG = ROOT / "results", ROOT / "fig"
ARMS = {"A": "arm_a.csv", "B": "arm_b.csv", "B'": "arm_b_refined.csv", "C": "arm_c.csv"}
LEVELS = ["facil", "intermedio", "dificil"]
COLORS = {"A": "#4c72b0", "B": "#dd8452", "B'": "#c44e52", "C": "#55a868"}


def load_csv(name):
    with open(RES / name, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def num(x):
    return float(x) if x not in ("", None) else None


def quart(xs):
    q = statistics.quantiles(xs, n=4, method="inclusive")
    return statistics.median(xs), q[0], q[2]


def failure_signal(arm, r):
    """Detectable-without-ground-truth signal for a failure."""
    if r["outcome"] == "correct":
        return None
    if arm in ("B", "B'"):
        return {"spec_error": "spec_error", "unsat": "unsat", "timeout": "timeout",
                "multiple": "multiple (alerta)", "unique": "silencioso"}.get(r["solver_status"], r["solver_status"])
    if arm == "C":
        return "formato" if r["error_message"] else "silencioso"
    return "silencioso"


def scorecard(data, price_in, price_out):
    rows = []
    for arm, rs in data.items():
        n = len(rs)
        correct = sum(r["outcome"] == "correct" for r in rs)
        wall = [num(r["wall_s"]) for r in rs]
        tin = sum(int(r["tokens_in"] or 0) for r in rs)
        tout = sum(int(r["tokens_out"] or 0) for r in rs)
        cost = (tin * price_in + tout * price_out) / 1e6
        fails = [failure_signal(arm, r) for r in rs if r["outcome"] != "correct"]
        loud = sum(f in ("spec_error", "unsat", "timeout", "formato") for f in fails)
        alert = sum(f == "multiple (alerta)" for f in fails)
        med, q1, q3 = quart(wall)
        rows.append({
            "arm": arm, "n": n, "correct": correct,
            "incorrect": sum(r["outcome"] == "incorrect" for r in rs),
            "no_answer": sum(r["outcome"] == "no_answer" for r in rs),
            "accuracy": correct / n,
            "wall_median_s": med, "wall_q1_s": q1, "wall_q3_s": q3, "wall_total_s": sum(wall),
            "llm_total_s": sum(num(r["llm_s"]) for r in rs),
            "solver_total_s": sum(num(r["solver_s"]) for r in rs),
            "tokens_in": tin, "tokens_out": tout,
            "tokens_median": statistics.median(int(r["tokens_in"] or 0) + int(r["tokens_out"] or 0) for r in rs),
            "cost_usd": cost,
            "cost_per_correct_usd": cost / correct if correct else "",
            "seconds_per_correct": sum(wall) / correct if correct else "",
            "failures": len(fails), "failures_detectable": loud, "failures_alert": alert,
            "failures_silent": len(fails) - loud - alert,
        })
    return rows


def by_difficulty(data):
    out = []
    for arm, rs in data.items():
        for lv in LEVELS:
            sub = [r for r in rs if r["difficulty"] == lv]
            out.append({"arm": arm, "difficulty": lv, "n": len(sub),
                        "correct": sum(r["outcome"] == "correct" for r in sub),
                        "accuracy": sum(r["outcome"] == "correct" for r in sub) / len(sub)})
    return out


def variance(solutions, levels):
    """Per-seed accuracy of the temperature-0.7 reruns, graded here."""
    runs = defaultdict(dict)  # arm -> seed -> {pid: outcome}
    for path in sorted((RES / "variance").glob("*.jsonl")):
        seed = path.stem.split("_s")[-1]
        for line in path.read_text(encoding="utf-8").splitlines():
            r = json.loads(line)
            runs[r["arm"]].setdefault(seed, {})[r["problem_id"]] = grade(r["answer"], solutions[r["problem_id"]])
    rows = []
    for arm, seeds in runs.items():
        complete = {s: o for s, o in seeds.items() if len(o) == len(solutions)}
        if not complete:
            continue
        accs = [sum(v == "correct" for v in o.values()) / len(o) for o in complete.values()]
        ever = sum(any(o[p] == "correct" for o in complete.values()) for p in solutions)
        row = {"arm": arm, "temperature": 0.7, "seeds": len(complete),
               "acc_mean": statistics.mean(accs), "acc_sd": statistics.stdev(accs) if len(accs) > 1 else 0,
               "acc_min": min(accs), "acc_max": max(accs), "problems_ever_correct": ever}
        for lv in LEVELS:
            pids = [p for p in solutions if levels[p] == lv]
            per = [sum(o[p] == "correct" for p in pids) / len(pids) for o in complete.values()]
            row[f"acc_{lv}_mean"] = statistics.mean(per)
            row[f"acc_{lv}_sd"] = statistics.stdev(per) if len(per) > 1 else 0
        rows.append(row)
    return rows


def c_failure_analysis(c_rows, models, solutions, statements):
    """Post-hoc (needs ground truth): how wrong is each C answer?"""
    out = []
    for r in c_rows:
        pid = r["problem_id"]
        ans = json.loads(r["answer"]) if r["answer"] else {}
        sol = solutions[pid]
        right = sum(str(ans.get(k)).upper() == str(v).upper() for k, v in sol.items())
        try:
            checks = check_assignment(models[pid], ans)
            violated = [cid for cid, _, ok in checks if not ok]
            total = len(checks)
        except Exception as exc:  # missing/odd values
            violated, total = [f"error:{type(exc).__name__}"], ""
        allowed = statements[pid]["allowed_values"]
        keys = statements[pid]["keys"]
        # "Echo" = the answer reproduces the order of allowed values / 1..n positions.
        echo = all(str(ans.get(k)).upper() == str(allowed[k][i % len(allowed[k])]).upper()
                   for i, k in enumerate(keys))
        out.append({"problem_id": pid, "difficulty": r["difficulty"], "outcome": r["outcome"],
                    "vars_correct": right, "vars_total": len(sol),
                    "checks_total": total,  # domain check + every hand-model constraint
                    "constraints_violated": len(violated), "violated_ids": " ".join(violated),
                    "format_signal": r["error_message"], "echo_of_domain_order": echo})
    return out


def write(rows, name):
    with open(RES / name, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def figures(data, diff, var):
    FIG.mkdir(exist_ok=True)
    # 1. Accuracy vs difficulty (required).
    fig, ax = plt.subplots(figsize=(10, 4.2))
    width = 0.2
    names = {"facil": "Fácil (7)", "intermedio": "Intermedio (7)", "dificil": "Difícil (6)"}
    for i, arm in enumerate(data):
        ys = [next(d["accuracy"] for d in diff if d["arm"] == arm and d["difficulty"] == lv) for lv in LEVELS]
        xs = [j + (i - 1.5) * width for j in range(3)]
        bars = ax.bar(xs, [100 * y for y in ys], width, label=f"{arm} (T=0)", color=COLORS[arm])
        ax.bar_label(bars, labels=[f"{100 * y:.0f} %" for y in ys], fontsize=7, padding=2)
        v = next((v for v in var if v["arm"] == arm), None)
        if v:
            ax.errorbar(xs, [100 * v[f"acc_{lv}_mean"] for lv in LEVELS],
                        yerr=[100 * v[f"acc_{lv}_sd"] for lv in LEVELS], fmt="D", ms=4,
                        color="black", capsize=3, lw=1,
                        label=f"{arm}: media ± d.e., T=0,7, {v['seeds']} semillas")
    ax.set_xticks(range(3), [names[lv] for lv in LEVELS])
    ax.set_ylabel("Precisión (%)")
    ax.set_ylim(0, 110)
    ax.set_title("Precisión por brazo y dificultad — qwen2.5:3b, 20 problemas CSP")
    ax.legend(fontsize=7.5, loc="upper left", bbox_to_anchor=(1.01, 1))
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "accuracy_vs_difficulty.png", dpi=150)
    plt.close(fig)

    # 2. Latency per instance, LLM vs solver (log scale).
    fig, ax = plt.subplots(figsize=(7, 4))
    for i, arm in enumerate(data):
        rs = data[arm]
        llm = statistics.median(num(r["llm_s"]) for r in rs)
        sol = statistics.median(num(r["solver_s"]) for r in rs)
        if llm:
            ax.bar(i - 0.17, llm, 0.34, color=COLORS[arm])
        if sol:
            ax.bar(i + 0.17, sol, 0.34, color=COLORS[arm], hatch="//", alpha=0.6)
        ax.text(i - 0.17, llm * 1.3 if llm else 2e-5, f"{llm:.3g} s" if llm else "sin LLM",
                ha="center", fontsize=7)
        ax.text(i + 0.17, sol * 1.3 if sol else 2e-5, f"{sol * 1000:.2g} ms" if sol else "sin solver",
                ha="center", fontsize=7)
    ax.set_yscale("log")
    ax.set_xticks(range(len(data)), list(data))
    ax.set_ylabel("Mediana por instancia (s, escala log)")
    ax.set_ylim(1e-5, 1e3)
    ax.set_title("Tiempo del LLM (sólido) vs. solver (rayado), mediana por instancia")
    fig.tight_layout()
    fig.savefig(FIG / "latency_by_arm.png", dpi=150)
    plt.close(fig)

    # 3. Failures by detectability signal, per arm.
    cats = ["spec_error", "unsat", "formato", "multiple (alerta)", "silencioso"]
    ccol = {"spec_error": "#8172b3", "unsat": "#937860", "formato": "#64b5cd",
            "multiple (alerta)": "#ccb974", "silencioso": "#c44e52"}
    fig, ax = plt.subplots(figsize=(7, 4))
    arms = [a for a in data if a != "A"]
    bottom = [0] * len(arms)
    for c in cats:
        vals = [sum(failure_signal(a, r) == c for r in data[a]) for a in arms]
        ax.bar(arms, vals, bottom=bottom, color=ccol[c], label=c)
        for j, v in enumerate(vals):
            if v:
                ax.text(j, bottom[j] + v / 2, str(v), ha="center", va="center", fontsize=8, color="white")
        bottom = [b + v for b, v in zip(bottom, vals)]
    ax.set_ylabel("Fallos (de 20)")
    ax.set_title("Fallos por señal disponible sin ground truth")
    ax.legend(fontsize=8, title="Señal", title_fontsize=8, loc="upper left", bbox_to_anchor=(1, 1))
    fig.tight_layout()
    fig.savefig(FIG / "errors_by_category.png", dpi=150)
    plt.close(fig)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--input-price", type=float, default=0.30)
    p.add_argument("--output-price", type=float, default=0.30)
    args = p.parse_args()
    data = {arm: load_csv(f) for arm, f in ARMS.items()}
    gt = json.loads((ROOT / "problems/ground_truth/ground_truth.json").read_text(encoding="utf-8"))["problems"]
    solutions = {g["id"]: g["solution"] for g in gt}
    models = {g["id"]: g["model"] for g in gt}
    levels = {g["id"]: g["difficulty"] for g in gt}
    public = json.loads((ROOT / "problems/public/problems.json").read_text(encoding="utf-8"))["problems"]
    formats = {q["id"]: q["answer_format"] for q in public}

    sc = scorecard(data, args.input_price, args.output_price)
    diff = by_difficulty(data)
    var = variance(solutions, levels)
    write(sc, "scorecard.csv")
    write(diff, "accuracy_by_difficulty.csv")
    if var:
        write(var, "variance_summary.csv")
    write(c_failure_analysis(data["C"], models, solutions, formats), "c_failure_analysis.csv")
    figures(data, diff, var)
    for r in sc:
        print(f"{r['arm']:>2}: {r['correct']}/{r['n']}  cost=${r['cost_usd']:.6f}  "
              f"per-correct={r['cost_per_correct_usd']}  detectable={r['failures_detectable']} "
              f"alert={r['failures_alert']} silent={r['failures_silent']}")
    for v in var:
        print(f"var {v['arm']}: {v['acc_mean']:.3f} ± {v['acc_sd']:.3f} over {v['seeds']} seeds")


if __name__ == "__main__":
    main()
