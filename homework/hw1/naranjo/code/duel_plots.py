"""The figures for Part 2 (the duel), one set per domain. Reads
``results/duel/<domain>/summary.csv``; writes PNGs into ``fig/``.

    fig7_duel_grid_scaling.png    fig10_duel_puzzle_scaling.png
        optimality rate vs size, three systems, 95 % Wilson CIs
    fig8_duel_grid_failures.png   fig11_duel_puzzle_failures.png
        the validator's categories per size, one panel per system
    fig9_duel_grid_latency.png    fig12_duel_puzzle_latency.png
        median latency (IQR bars) and output tokens vs size

Run: ``python duel_plots.py`` (after ``python duel.py``).
"""

from __future__ import annotations

import csv
from math import sqrt
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results" / "duel"
FIG = ROOT / "fig"

DOMAINS = {
    "grid": {"summary": "grid/summary.csv", "sizes": [5, 8, 12, 16],
             "tick": lambda n: f"{n}x{n}", "xlabel": "grid size",
             "noun": "problem size",
             "figs": ("fig7_duel_grid_scaling.png", "fig8_duel_grid_failures.png",
                      "fig9_duel_grid_latency.png")},
    "puzzle": {"summary": "puzzle/summary.csv", "sizes": [4, 8, 12, 16],
               "tick": str, "xlabel": "8-puzzle optimal solution depth",
               "noun": "solution depth",
               "figs": ("fig10_duel_puzzle_scaling.png",
                        "fig11_duel_puzzle_failures.png",
                        "fig12_duel_puzzle_latency.png")},
}
SYSTEMS = ["A*", "LLM", "LLM+tool"]
COLORS = {"A*": "#8c564b", "LLM": "#d62728", "LLM+tool": "#1f77b4"}
MARKERS = {"A*": "P", "LLM": "o", "LLM+tool": "s"}
LABELS = {"A*": "A* + Manhattan", "LLM": "qwen2.5:3b (bare)",
          "LLM+tool": "qwen2.5:3b + A* tool"}
CATS = [("optimal", "#2ca02c", "optimal"),
        ("wrong_cost", "#bcbd22", "3: optimal path, wrong reported cost"),
        ("suboptimal", "#ff7f0e", "2: legal but suboptimal"),
        ("illegal", "#d62728", "1: illegal path"),
        ("malformed", "#7f7f7f", "unparseable output")]


def _read(name):
    with (RESULTS / name).open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def wilson(k, n, z=1.96):
    """95 % Wilson interval — honest at n = 10 and at k = 0 or k = n,
    where the normal approximation collapses to a zero-width bar."""
    if n == 0:
        return 0.0, 0.0
    p = k / n
    den = 1 + z * z / n
    mid = (p + z * z / (2 * n)) / den
    half = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return max(0.0, mid - half), min(1.0, mid + half)


def _summary(name):
    # The puzzle summary also holds the archived v1 prompt run; figures show
    # the main run only (v2, or no prompt column at all for the grid).
    rows = [r for r in _read(name)
            if r["size"] != "all" and r.get("prompt", "v2") == "v2"]
    return {(r["system"], int(r["size"])): r for r in rows}


def fig_scaling(summ, d):
    SIZES = d["sizes"]
    fig, ax = plt.subplots(figsize=(7, 4.5))
    offset = {"A*": -0.25, "LLM": 0.0, "LLM+tool": 0.25}
    for s in SYSTEMS:
        xs, ys, lo, hi = [], [], [], []
        for size in SIZES:
            r = summ.get((s, size))
            if r is None:
                continue
            k, n = int(r["n_optimal"]), int(r["n"])
            a, b = wilson(k, n)
            xs.append(size + offset[s]); ys.append(k / n)
            lo.append(k / n - a); hi.append(b - k / n)
        ax.errorbar(xs, ys, yerr=[lo, hi], color=COLORS[s], marker=MARKERS[s],
                    capsize=4, lw=2, ms=8, label=LABELS[s])
    ax.set_xticks(SIZES, [d["tick"](n) for n in SIZES])
    ax.set_ylim(-0.05, 1.05)
    ax.set_xlabel(f"{d['xlabel']} (10 instances each)")
    ax.set_ylabel("fraction optimal (validator)")
    ax.set_title(f"Optimality rate vs {d['noun']} (bars: 95% Wilson CI, n = 10)")
    ax.grid(alpha=.3)
    ax.legend(loc="center")
    fig.tight_layout()
    fig.savefig(FIG / d["figs"][0], dpi=150)
    plt.close(fig)


def fig_failures(summ, d):
    SIZES = d["sizes"]
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.2), sharey=True)
    for ax, s in zip(axes, SYSTEMS):
        bottom = [0] * len(SIZES)
        for cat, color, label in CATS:
            vals = [int(summ[(s, n)][f"n_{cat}"]) if (s, n) in summ else 0 for n in SIZES]
            ax.bar([d["tick"](n) for n in SIZES], vals, bottom=bottom,
                   color=color, label=label, edgecolor="white")
            bottom = [b + v for b, v in zip(bottom, vals)]
        ax.set_title(LABELS[s])
        ax.set_xlabel(d["xlabel"])
    axes[0].set_ylabel("instances (of 10)")
    axes[-1].legend(loc="upper left", bbox_to_anchor=(1.01, 1), fontsize=8)
    fig.suptitle("How each system fails — categories assigned by our validator, never by the model")
    fig.tight_layout()
    fig.savefig(FIG / d["figs"][1], dpi=150, bbox_inches="tight")
    plt.close(fig)


def fig_latency(summ, d):
    SIZES = d["sizes"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.2))
    for s in SYSTEMS:
        pts = [(n, summ[(s, n)]) for n in SIZES if (s, n) in summ]
        x = [n for n, _ in pts]
        med = [float(r["seconds_median"]) for _, r in pts]
        q1 = [float(r["seconds_q1"]) for _, r in pts]
        q3 = [float(r["seconds_q3"]) for _, r in pts]
        a1.errorbar(x, med, yerr=[[m - a for m, a in zip(med, q1)],
                                  [b - m for m, b in zip(med, q3)]],
                    color=COLORS[s], marker=MARKERS[s], capsize=4, lw=2,
                    label=LABELS[s])
        if s != "A*":
            tok = [float(r["tokens_out_median"]) for _, r in pts]
            t1 = [float(r["tokens_out_q1"]) for _, r in pts]
            t3 = [float(r["tokens_out_q3"]) for _, r in pts]
            a2.errorbar(x, tok, yerr=[[m - a for m, a in zip(tok, t1)],
                                      [b - m for m, b in zip(tok, t3)]],
                        color=COLORS[s], marker=MARKERS[s], capsize=4, lw=2,
                        label=LABELS[s])
    a1.set_yscale("log")
    a1.set_title("Wall-clock per instance (median, IQR bars; log y)")
    a1.set_ylabel("seconds")
    a2.set_title("Output tokens per instance (median, IQR bars)")
    a2.set_ylabel("tokens generated")
    for ax in (a1, a2):
        ax.set_xticks(SIZES, [d["tick"](n) for n in SIZES])
        ax.set_xlabel(d["xlabel"])
        ax.grid(alpha=.3)
        ax.legend()
    fig.tight_layout()
    fig.savefig(FIG / d["figs"][2], dpi=150)
    plt.close(fig)


def main():
    FIG.mkdir(exist_ok=True)
    for name, d in DOMAINS.items():
        if not (RESULTS / d["summary"]).exists():
            print(f"skip {name}: results/duel/{d['summary']} not found")
            continue
        summ = _summary(d["summary"])
        fig_scaling(summ, d)
        fig_failures(summ, d)
        fig_latency(summ, d)
        print("wrote " + ", ".join(d["figs"]))


if __name__ == "__main__":
    main()
