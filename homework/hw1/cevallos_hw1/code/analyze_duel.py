"""Part 2 analysis: tables + figures + numbers for the scorecard.

    python analyze_duel.py

Reads  results/duel_raw.csv, duel_repro.csv, puzzle_raw.csv, grid_raw.csv,
       reference_optimal.csv
Writes results/duel_summary.csv, results/duel_scorecard_numbers.json,
       fig/duel_scaling.png, fig/duel_failures.png
"""
import csv
import json
import math
import statistics as st
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from duel_common import FIG_DIR, RESULTS_DIR

CATS = ["optimal_correct", "wrong_cost", "suboptimal", "illegal"]
COLORS = {"Classical A*": "#1b6ca8", "LLM": "#d1495b", "LLM+A*": "#2a9d5c"}


def rd(name):
    p = RESULTS_DIR / name
    if not p.exists():
        return []
    with open(p, newline="") as f:
        return list(csv.DictReader(f))


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def med_iqr(xs):
    xs = sorted(x for x in xs if x is not None)
    if not xs:
        return ("", "", "")
    q = st.quantiles(xs, n=4) if len(xs) >= 2 else [xs[0]] * 3
    return (st.median(xs), q[0], q[2])


def fl(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def tb(x):
    return str(x) == "True"


def classical_rows():
    """Classical A* (Manhattan) judged by the SAME standard as the LLM:
    solved inside the timeout AND cost equals the reference optimum."""
    ref = {(r["domain"], int(r["level"]), int(r["instance"])): int(r["optimal_cost"])
           for r in rd("reference_optimal.csv")}
    out = []
    for fn, dom in (("puzzle_raw.csv", "puzzle"), ("grid_raw.csv", "grid")):
        for r in rd(fn):
            if r["algorithm"] != "A*_Manhattan":
                continue
            lvl, i = int(r["difficulty"]), int(r["instance"])
            ok = r["status"] == "solved" and fl(r["cost"]) == ref.get((dom, lvl, i))
            out.append(dict(system="Classical A*", model="A*_Manhattan", domain=dom,
                            level=lvl, instance=i, optimal=ok,
                            category="optimal_correct" if ok else "timeout_or_fail",
                            latency_s=fl(r["time_seconds"]), in_tokens=None, out_tokens=None))
    return out


def main():
    FIG_DIR.mkdir(exist_ok=True)
    raw = rd("duel_raw.csv")
    if not raw:
        print("no results/duel_raw.csv yet -- run run_duel.py first")
        return
    for r in raw:
        r["level"], r["instance"] = int(r["level"]), int(r["instance"])
        r["optimal"] = tb(r["optimal"])
        r["latency_s"] = fl(r["latency_s"])
        r["in_tokens"], r["out_tokens"] = fl(r["in_tokens"]), fl(r["out_tokens"])
    rows = classical_rows() + raw

    groups = defaultdict(list)
    for r in rows:
        name = r["system"] if r["system"] == "Classical A*" else f"{r['system']} [{r['model']} T={r.get('temperature', '')}]"
        groups[(name, r["system"], r["domain"], r["level"])].append(r)

    summary, scorecard = [], {}
    for (name, sysname, dom, lvl), rs in sorted(groups.items()):
        n = len(rs)
        cnt = {c: sum(r["category"] == c for r in rs) for c in CATS}
        k_opt = sum(r["optimal"] for r in rs)
        lo, hi = wilson(k_opt, n)
        lat = med_iqr([r["latency_s"] for r in rs])
        summary.append(dict(
            system=name, domain=dom, level=lvl, n=n,
            optimal_path=k_opt, optimal_rate=round(k_opt / n, 3),
            ci95_lo=round(lo, 3), ci95_hi=round(hi, 3),
            optimal_correct=cnt["optimal_correct"], wrong_cost=cnt["wrong_cost"],
            suboptimal=cnt["suboptimal"], illegal=cnt["illegal"],
            timeout_or_fail=sum(r["category"] == "timeout_or_fail" for r in rs),
            lat_median=lat[0], lat_q1=lat[1], lat_q3=lat[2],
            tokens_total=sum((r["in_tokens"] or 0) + (r["out_tokens"] or 0) for r in rs)))
    keys = list(summary[0].keys())
    with open(RESULTS_DIR / "duel_summary.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(summary)

    # ---- totals per system (scorecard feed) --------------------------------
    tot = defaultdict(list)
    for (name, sysname, dom, lvl), rs in groups.items():
        tot[(name, dom)] += rs
        tot[(name, "ALL")] += rs
    for (name, dom), rs in sorted(tot.items()):
        n = len(rs)
        scorecard.setdefault(name, {})[dom] = dict(
            n=n,
            optimal_rate=sum(r["optimal"] for r in rs) / n,
            optimal_correct=sum(r["category"] == "optimal_correct" for r in rs),
            wrong_cost=sum(r["category"] == "wrong_cost" for r in rs),
            suboptimal=sum(r["category"] == "suboptimal" for r in rs),
            illegal=sum(r["category"] == "illegal" for r in rs),
            timeouts=sum(r["category"] == "timeout_or_fail" for r in rs),
            median_latency_s=med_iqr([r["latency_s"] for r in rs])[0],
            total_tokens=sum((r["in_tokens"] or 0) + (r["out_tokens"] or 0) for r in rs),
            tool_calls_mean=(st.mean(fl(r.get("tool_calls")) or 0 for r in rs)
                             if "tool_calls" in rs[0] else None),
            tool_args_wrong=(sum(r.get("tool_args_correct") == "False" for r in rs)
                             if "tool_calls" in rs[0] else None),
        )

    # ---- reproducibility ----------------------------------------------------
    rep = rd("duel_repro.csv")
    repro = defaultdict(lambda: defaultdict(list))
    for r in rep:
        repro[(r["system"], r["model"], r["temperature"])][r["domain"]].append(r)
    repro_out = {}
    for k, doms in repro.items():
        for dom, rs in doms.items():
            repro_out[f"{k[0]}|{k[1]}|T={k[2]}|{dom}"] = dict(
                calls=len(rs),
                distinct_answers=len({r["answer_key"] for r in rs}),
                categories=[r["category"] for r in rs])
    scorecard["_reproducibility"] = repro_out
    (RESULTS_DIR / "duel_scorecard_numbers.json").write_text(json.dumps(scorecard, indent=2))

    # ---- figure 1: scaling (optimality rate vs size) -------------------------
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
    for ax, dom, title, xl in ((axes[0], "puzzle", "8-puzzle", "optimal solution depth"),
                               (axes[1], "grid", "Weighted grid", "grid side length")):
        for name in sorted({s["system"] for s in summary}):
            pts = sorted((s["level"], s["optimal_rate"], s["ci95_lo"], s["ci95_hi"])
                         for s in summary if s["system"] == name and s["domain"] == dom)
            if not pts:
                continue
            base = name.split(" [")[0]
            x = [p[0] for p in pts]
            ax.plot(x, [p[1] for p in pts], "o-", label=name, color=COLORS.get(base))
            ax.fill_between(x, [p[2] for p in pts], [p[3] for p in pts],
                            alpha=0.12, color=COLORS.get(base))
        ax.set_title(title)
        ax.set_xlabel(xl)
        ax.set_xticks(sorted({s["level"] for s in summary if s["domain"] == dom}))
        ax.set_ylim(-0.03, 1.05)
        ax.grid(alpha=.3)
    axes[0].set_ylabel("fraction of instances solved optimally\n(shaded: 95% Wilson CI, n=10)")
    axes[1].legend(fontsize=7, loc="lower left")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "duel_scaling.png", dpi=150)
    plt.close(fig)

    # ---- figure 2: failure categories per size --------------------------------
    names = sorted({s["system"] for s in summary if s["system"] != "Classical A*"})
    if names:
        fig, axes = plt.subplots(len(names), 2, figsize=(10, 3 * len(names)), squeeze=False)
        pal = {"optimal_correct": "#2a9d5c", "wrong_cost": "#e9c46a",
               "suboptimal": "#f4a261", "illegal": "#d1495b"}
        for i, name in enumerate(names):
            for j, dom in enumerate(("puzzle", "grid")):
                ax = axes[i][j]
                ss = sorted((s for s in summary if s["system"] == name and s["domain"] == dom),
                            key=lambda s: s["level"])
                bottom = [0] * len(ss)
                for c in CATS:
                    vals = [s[c] for s in ss]
                    ax.bar([str(s["level"]) for s in ss], vals, bottom=bottom,
                           label=c, color=pal[c])
                    bottom = [b + v for b, v in zip(bottom, vals)]
                ax.set_title(f"{name} -- {dom}", fontsize=8)
                ax.set_ylabel("instances")
        axes[0][0].legend(fontsize=7)
        fig.tight_layout()
        fig.savefig(FIG_DIR / "duel_failures.png", dpi=150)
        plt.close(fig)

    # ---- console report -----------------------------------------------------
    print(f"{'system':44}{'dom':7}{'lvl':>4}{'n':>3} {'opt':>4} {'wcost':>5} {'subopt':>6} {'illeg':>5}  rate [95% CI]")
    for s in summary:
        print(f"{s['system'][:43]:44}{s['domain']:7}{s['level']:>4}{s['n']:>3} "
              f"{s['optimal_correct']:>4} {s['wrong_cost']:>5} {s['suboptimal']:>6} {s['illegal']:>5}  "
              f"{s['optimal_rate']:.2f} [{s['ci95_lo']:.2f},{s['ci95_hi']:.2f}]")
    for k, v in repro_out.items():
        print(f"REPRO {k}: {v['distinct_answers']} distinct answers / {v['calls']} calls")
    print("\nwrote results/duel_summary.csv, results/duel_scorecard_numbers.json, "
          "fig/duel_scaling.png, fig/duel_failures.png")


if __name__ == "__main__":
    main()
