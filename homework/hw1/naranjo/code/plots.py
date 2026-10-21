"""The figures for Part 1 (at least 3 required — six are produced).

Reads ``results/summary.csv`` (medians + IQRs), ``results/raw_*.csv``,
``results/bstar.csv`` and ``results/analysis*.csv``; writes PNGs into ``fig/``.

    fig1_expansions_puzzle.png   expansions vs solution depth, log y (the growth curve)
    fig2_expansions_grid.png     expansions vs grid size, log y, timeouts marked
    fig3_dominance.png           Manhattan vs misplaced expansions, y = x line
    fig4_inadmissible.png        h x 3: speedup on the left, solution-quality cost on the right
    fig5_bstar.png               effective branching factor per heuristic
    fig6_wallclock.png           median wall-clock, both domains

Run: ``python3 plots.py``
"""

from __future__ import annotations

import csv
import statistics
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
FIG = ROOT / "fig"

SIZES = {"puzzle": [4, 8, 12, 16], "grid": [5, 8, 12, 16]}
LEVEL_LABEL = {"puzzle": "solution depth", "grid": "grid size"}
COLORS = {
    "BFS": "#1f77b4", "DFS": "#ff7f0e", "UCS": "#2ca02c", "IDS": "#d62728",
    "A*+misplaced": "#9467bd", "A*+manhattan": "#8c564b",
    "A*+3xmanhattan": "#e377c2", "A*+8xmanhattan": "#17becf",
}
MARKERS = {
    "BFS": "o", "DFS": "s", "UCS": "^", "IDS": "D",
    "A*+misplaced": "v", "A*+manhattan": "P",
    "A*+3xmanhattan": "*", "A*+8xmanhattan": "X",
}


def _summary() -> list[dict]:
    with (RESULTS / "summary.csv").open(newline="") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        r["size"] = int(r["size"])
        for k in list(r):
            if k.endswith(("_median", "_q1", "_q3")) or k.startswith("n_"):
                r[k] = float(r[k]) if r[k] else None
    return rows


def _raw(domain) -> list[dict]:
    with (RESULTS / f"raw_{domain}.csv").open(newline="") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        r["size"] = int(r["size"])
        r["instance"] = int(r["instance"])
        r["expansions"] = int(r["expansions"])
        r["max_frontier"] = int(r["max_frontier"])
        r["seconds"] = float(r["seconds"])
        r["cost"] = int(r["cost"]) if r["cost"] else None
        r["length"] = int(r["length"]) if r["length"] else None
    return rows


def _algos(rows, domain):
    """Order the legend so it reads BFS, DFS, UCS, IDS, then the A* variants."""
    seen = []
    for r in rows:
        if r["domain"] == domain and r["algorithm"] not in seen:
            seen.append(r["algorithm"])
    order = ["BFS", "DFS", "UCS", "IDS", "A*+zero", "A*+misplaced",
             "A*+manhattan", "A*+3xmanhattan", "A*+8xmanhattan"]
    return sorted(seen, key=lambda a: order.index(a) if a in order else 99)


def _panel_expansions(rows, domain, ax, metric="expansions", logy=True, title=""):
    sizes = SIZES[domain]
    missing = []
    for algo in _algos(rows, domain):
        xs, ys, lo, hi = [], [], [], []
        for size in sizes:
            g = [r for r in rows if r["domain"] == domain
                 and r["size"] == size and r["algorithm"] == algo]
            if not g:
                continue
            r = g[0]
            if r["n_timeout"]:
                missing.append((algo, size, r["n_timeout"], r["n_solved"]))
            if r[f"{metric}_median"] is None:
                continue                      # every run timed out: no median
            xs.append(size)
            ys.append(r[f"{metric}_median"])
            lo.append(r[f"{metric}_median"] - (r[f"{metric}_q1"] or 0))
            hi.append((r[f"{metric}_q3"] or 0) - r[f"{metric}_median"])
        if not xs:
            continue
        ax.errorbar(xs, ys, yerr=[lo, hi], label=algo, color=COLORS.get(algo),
                    marker=MARKERS.get(algo, "o"), capsize=3, lw=1.6, ms=6)
    if logy:
        ax.set_yscale("log")
    ax.set_xlabel(LEVEL_LABEL[domain])
    ax.set_ylabel(f"median {metric} (log)" if logy else f"median {metric}")
    ax.set_title(title, fontsize=10)
    ax.grid(True, which="both", alpha=0.3)
    if missing:
        note = "; ".join(
            f"{a} @{s}: {int(t)} timeout(s), {int(n)} solved"
            for a, s, t, n in missing)
        ax.annotate("timeouts: " + note, xy=(0.02, 0.02),
                    xycoords="axes fraction", fontsize=7, color="#d62728")


def fig1(rows):
    fig, ax = plt.subplots(figsize=(7.5, 5))
    _panel_expansions(rows, "puzzle", ax, title="8-puzzle — node expansions vs solution depth (median, IQR)")
    ax.legend(fontsize=8, ncol=2)
    fig.suptitle("Uninformed search grows exponentially; a good heuristic does not",
                 fontsize=11)
    fig.tight_layout()
    p = FIG / "fig1_expansions_puzzle.png"
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  {p}")


def fig2(rows):
    fig, ax = plt.subplots(figsize=(7.5, 5))
    _panel_expansions(rows, "grid", ax,
                      title="Weighted grid — node expansions vs grid size (median, IQR)")
    ax.legend(fontsize=8, ncol=2)
    fig.suptitle("Small state spaces stay small; the guarantee, not the cost, is what changes",
                 fontsize=11)
    fig.tight_layout()
    p = FIG / "fig2_expansions_grid.png"
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  {p}")


def fig3(rows):
    """Dominance: every point must sit on or below the y = x line."""
    groups = {}
    for r in _raw("puzzle"):
        if r["algorithm"] in ("A*+manhattan", "A*+misplaced") and r["cost"] is not None:
            groups.setdefault((r["size"], r["instance"]), {})[r["algorithm"]] = r
    mis = [g["A*+misplaced"]["expansions"] for g in groups.values()
           if "A*+misplaced" in g and "A*+manhattan" in g]
    man = [g["A*+manhattan"]["expansions"] for g in groups.values()
           if "A*+misplaced" in g and "A*+manhattan" in g]

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(mis, man, s=42, color="#8c564b", zorder=3,
               label="40 instances (depths 4-16)")
    lim = [min(mis + man) * 0.8, max(mis + man) * 1.25]
    ax.plot(lim, lim, "--", color="black", lw=1.2, label="y = x  (equal expansions)")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("A* + misplaced-tiles: node expansions")
    ax.set_ylabel("A* + Manhattan: node expansions")
    ax.set_title("Heuristic dominance: Manhattan never expands more than misplaced",
                 fontsize=11)
    ax.legend(fontsize=9)
    ax.grid(True, which="both", alpha=0.3)
    n_above = sum(1 for a, b in zip(mis, man) if b > a)
    ax.annotate(f"{n_above} points above the line (must be 0)",
                xy=(0.03, 0.95), xycoords="axes fraction", fontsize=9)
    fig.tight_layout()
    p = FIG / "fig3_dominance.png"
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  {p}")


def fig4(rows):
    """h x 3: what the speedup bought, and what it cost."""
    with (RESULTS / "analysis3_inadmissible.csv").open(newline="") as fh:
        data = [r for r in csv.DictReader(fh) if r["domain"] == "puzzle"]
    for r in data:
        r["size"] = int(r["size"])
        r["cost_gap_vs_optimum"] = int(float(r["cost_gap_vs_optimum"]))
        r["suboptimal"] = r["suboptimal"].strip().lower() in ("true", "1", "yes")
        r["speedup_expansions"] = float(r["speedup_expansions"]) \
            if r["speedup_expansions"] else None

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5))
    sizes = SIZES["puzzle"]
    sp, gap_max, gap_med, pct = [], [], [], []
    for size in sizes:
        sel = [r for r in data if r["size"] == size]
        s = [r["speedup_expansions"] for r in sel if r["speedup_expansions"]]
        sp.append(statistics.median(s) if s else float("nan"))
        g = [r["cost_gap_vs_optimum"] for r in sel]
        gap_max.append(max(g))
        gap_med.append(statistics.median(g))
        pct.append(100 * sum(1 for r in sel if r["suboptimal"]) / len(sel))

    ax1.plot(sizes, sp, "o-", color="#e377c2", lw=1.8)
    ax1.axhline(1.0, color="black", ls="--", lw=1)
    ax1.set_xlabel("solution depth")
    ax1.set_ylabel("expansion speedup vs A* + Manhattan")
    ax1.set_title("Speedup from h x 3 (above 1 = faster)", fontsize=10)
    ax1.grid(alpha=0.3)

    ax2.bar([s - 0.6 for s in sizes], gap_max, width=1.2, color="#d62728",
            label="worst gap", alpha=0.75)
    ax2.plot(sizes, gap_med, "o-", color="black", lw=1.6, label="median gap")
    ax2.set_xlabel("solution depth")
    ax2.set_ylabel("moves above the optimum")
    ax2.set_title("Cost of h x 3 (0 = still optimal)", fontsize=10)
    ax2.legend(fontsize=8)
    ax2.grid(alpha=0.3, axis="y")
    for x, y in zip(sizes, pct):
        ax2.annotate(f"{y:.0f}% bad", xy=(x, 0.15), ha="center", fontsize=8,
                     color="#d62728")

    fig.suptitle("h × 3: what it cost in solution quality, and what it bought "
                 "in speed (the honest answer is \"not much\")",
                 fontsize=11)
    fig.tight_layout()
    p = FIG / "fig4_inadmissible.png"
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  {p}")


def fig5():
    with (RESULTS / "bstar.csv").open(newline="") as fh:
        data = list(csv.DictReader(fh))
    for r in data:
        r["size"] = int(r["size"])
        for k in ("bstar_median", "bstar_q1", "bstar_q3"):
            r[k] = float(r[k])

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))
    for ax, domain in zip(axes, ("puzzle", "grid")):
        algos = _algos([{"domain": domain, "algorithm": r["algorithm"]}
                        for r in data if r["domain"] == domain], domain)
        for algo in algos:
            sel = sorted([r for r in data if r["domain"] == domain
                          and r["algorithm"] == algo], key=lambda r: r["size"])
            if not sel:
                continue
            xs = [r["size"] for r in sel]
            ys = [r["bstar_median"] for r in sel]
            lo = [r["bstar_median"] - r["bstar_q1"] for r in sel]
            hi = [r["bstar_q3"] - r["bstar_median"] for r in sel]
            ax.errorbar(xs, ys, yerr=[lo, hi], marker=MARKERS.get(algo, "o"),
                        color=COLORS.get(algo), capsize=3, lw=1.6, ms=6, label=algo)
        ax.axhline(1.0, color="black", ls="--", lw=1)
        ax.set_xlabel(LEVEL_LABEL[domain])
        ax.set_ylabel("effective branching factor b* (median, IQR)")
        ax.set_title(domain, fontsize=10)
        ax.grid(alpha=0.3)
        ax.set_ylim(bottom=0.9)
    axes[0].legend(fontsize=7, ncol=2)
    fig.suptitle("b* near 1 means the search went almost straight to the goal — "
                 "the question is whether it stays there", fontsize=11)
    fig.tight_layout()
    p = FIG / "fig5_bstar.png"
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  {p}")


def fig6(rows):
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))
    for ax, domain in zip(axes, ("puzzle", "grid")):
        _panel_expansions(rows, domain, ax, metric="seconds",
                          title=f"{domain} — median wall-clock (log)")
    axes[0].legend(fontsize=7, ncol=2)
    fig.suptitle("Latency is not where classical search loses: the cost curve is "
                 "predictable and monotone", fontsize=11)
    fig.tight_layout()
    p = FIG / "fig6_wallclock.png"
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  {p}")


def main():
    FIG.mkdir(exist_ok=True)
    rows = _summary()
    print("figures:")
    fig1(rows)
    fig2(rows)
    fig3(rows)
    fig4(rows)
    fig5()
    fig6(rows)


if __name__ == "__main__":
    main()
