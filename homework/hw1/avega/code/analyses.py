"""The four required analyses of Part 1. Reads ``results/raw_*.csv``.

    1. optimality    UCS == A*(admissible) everywhere; BFS is NOT optimal on
                      non-uniform costs — and here is the instance that proves it
    2. dominance     A*+manhattan expands no more nodes than A*+misplaced, on
                      every instance (a counterexample means a heuristic bug)
    3. inadmissible  h x 3: the speedup AND the solution-quality cost, both
                      numbers or the analysis is incomplete
    4. b*            effective branching factor per heuristic, per depth

Run: ``python3 analyses.py``. Each analysis prints its conclusion and writes a
CSV into ``results/``.
"""

from __future__ import annotations

import csv
import json
import random
import statistics
from pathlib import Path

from gridworld import GridProblem, load_instances as load_grids
from search import EightPuzzle, TinyGraph

import starter as s

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
SIZES = {"puzzle": [4, 8, 12, 16], "grid": [5, 8, 12, 16]}


# ---- shared helpers ---------------------------------------------------------

def load_rows() -> list[dict]:
    rows = []
    for domain in ("puzzle", "grid"):
        path = RESULTS / f"raw_{domain}.csv"
        if not path.exists():
            raise SystemExit(f"missing {path} — run harness.py first")
        with path.open(newline="") as fh:
            for r in csv.DictReader(fh):
                r["size"] = int(r["size"])
                r["instance"] = int(r["instance"])
                for k in ("cost", "length"):
                    r[k] = int(r[k]) if r[k] else None
                for k in ("expansions", "generated", "max_frontier"):
                    r[k] = int(r[k])
                r["seconds"] = float(r["seconds"])
                rows.append(r)
    return rows


def by_instance(rows, domain):
    """{(size, instance): {algorithm: row}}"""
    out: dict[tuple, dict] = {}
    for r in rows:
        if r["domain"] == domain and r["status"] == "solved":
            out.setdefault((r["size"], r["instance"]), {})[r["algorithm"]] = r
    return out


def _med(vals):
    return statistics.median(vals) if vals else float("nan")


def _iqr(vals):
    if not vals:
        return float("nan"), float("nan")
    if len(vals) == 1:
        return vals[0], vals[0]
    q1, _, q3 = statistics.quantiles(vals, n=4, method="inclusive")
    return q1, q3


def _write(name: str, fieldnames: list[str], rows: list[dict]) -> Path:
    path = RESULTS / name
    with path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print(f"  -> {path}")
    return path


# ---- analysis 1: optimality -------------------------------------------------

ANALYSIS1_FIELDS = [
    "domain", "size", "instance", "ucs_cost", "astar_manhattan",
    "astar_misplaced", "bfs_cost", "ids_cost", "dfs_cost",
    "admissible_equals_ucs", "bfs_equals_ucs", "ids_equals_ucs",
    "dfs_suboptimal", "bfs_suboptimal_by", "dfs_suboptimal_by",
]


def _a1_row(**kw) -> dict:
    """Every row gets every column (CSV writers are unforgiving)."""
    row = {f: "" for f in ANALYSIS1_FIELDS}
    row.update(kw)
    return row


def render_grid_with_paths(grid, path_a, path_b, cost_a, cost_b,
                           label_a="BFS", label_b="UCS"):
    """ASCII picture of the witness instance: cells on path A show 'a', cells on
    path B show 'b', cells on both show 'x', everything else keeps its terrain."""
    from gridworld import MOVES

    def cells(path):
        r, c = GridProblem(grid).initial
        seen = {(r, c)}
        for ch in path:
            dr, dc = MOVES[ch]
            r, c = r + dr, c + dc
            seen.add((r, c))
        return seen

    a, b = cells(path_a), cells(path_b)
    lines = [f"  cells on both paths = 'x', only {label_a} = 'a', "
             f"only {label_b} = 'b'"]
    for r, grow in enumerate(grid):
        out = []
        for c, ch in enumerate(grow):
            if (r, c) in a and (r, c) in b:
                out.append("x")
            elif (r, c) in a:
                out.append("a")
            elif (r, c) in b:
                out.append("b")
            else:
                out.append(ch)
        lines.append("  " + " ".join(out))
    lines.append(f"  {label_a}: moves={''.join(path_a)!r} -> cost {cost_a}")
    lines.append(f"  {label_b}: moves={''.join(path_b)!r} -> cost {cost_b}")
    return lines


def analysis1(rows):
    print("\n=== Analysis 1 — optimality of UCS / A*, and where BFS fails ===")
    out_rows = []

    # (a) 8-puzzle: every step costs 1, so BFS, IDS, UCS and A* with an
    #     admissible h must all return the SAME cost.
    mismatches = []
    for (size, inst), group in sorted(by_instance(rows, "puzzle").items()):
        costs = {a: group[a]["cost"] for a in group}
        ucs = costs.get("UCS")
        admissible = [costs.get("A*+manhattan"), costs.get("A*+misplaced")]
        equal = all(c == ucs for c in admissible if c is not None)
        bfs_eq = costs.get("BFS") == ucs
        ids_eq = costs.get("IDS") == ucs
        if not (equal and bfs_eq and ids_eq):
            mismatches.append((size, inst, costs))
        out_rows.append(_a1_row(
            domain="puzzle", size=size, instance=inst, ucs_cost=ucs,
            astar_manhattan=costs.get("A*+manhattan"),
            astar_misplaced=costs.get("A*+misplaced"),
            bfs_cost=costs.get("BFS"), ids_cost=costs.get("IDS"),
            dfs_cost=costs.get("DFS"),
            admissible_equals_ucs=equal, bfs_equals_ucs=bfs_eq,
            ids_equals_ucs=ids_eq,
            dfs_suboptimal=(costs.get("DFS") or ucs) > ucs,
            dfs_suboptimal_by=((costs.get("DFS") or ucs) - ucs),
        ))
    print(f"  puzzle (uniform cost): A*(admissible) == UCS == BFS == IDS on "
          f"{40 - len(mismatches)}/40 instances; mismatches: {len(mismatches)}")
    dfs_bad = sum(1 for r in out_rows if r["dfs_suboptimal"])
    print(f"  puzzle: DFS returned a longer-than-optimal path on {dfs_bad}/40 "
          f"(it never claimed optimality)")

    # (b) weighted grid: UCS == A*(manhattan); BFS is the one that breaks.
    grid_bfs_worse = []
    for (size, inst), group in sorted(by_instance(rows, "grid").items()):
        ucs = group.get("UCS", {}).get("cost")
        astar = group.get("A*+manhattan", {}).get("cost")
        bfs = group.get("BFS", {}).get("cost")
        ids = group.get("IDS", {}).get("cost")   # None when IDS timed out
        if ucs is None:
            continue
        row = _a1_row(
            domain="grid", size=size, instance=inst, ucs_cost=ucs,
            astar_manhattan=astar, bfs_cost=bfs,
            ids_cost=(ids if ids is not None else ""),
            dfs_cost=(group.get("DFS", {}).get("cost") or ""),
            admissible_equals_ucs=astar == ucs,
            bfs_equals_ucs=bfs == ucs,
            # blank when IDS timed out: no solution, so "equal?" has no answer
            ids_equals_ucs=(ids == ucs) if ids is not None else "",
            dfs_suboptimal=((group.get("DFS", {}).get("cost") or ucs) > ucs),
            bfs_suboptimal_by=(bfs - ucs) if bfs is not None else "",
            dfs_suboptimal_by=((group.get("DFS", {}).get("cost") or ucs) - ucs),
        )
        out_rows.append(row)
        if bfs is not None and bfs > ucs:
            grid_bfs_worse.append(((bfs - ucs) / ucs, size, inst, row))
    n_grid = sum(1 for r in out_rows if r["domain"] == "grid")
    print(f"  grid (non-uniform cost): A*+manhattan == UCS on "
          f"{sum(1 for r in out_rows if r['domain'] == 'grid' and r['admissible_equals_ucs'])}/{n_grid}, "
          f"but BFS > UCS on {len(grid_bfs_worse)}/{n_grid}")

    # IDS is a shallowest-path search, not a cheapest-path one: on the grid it
    # reproduces BFS's answer (same cost, same length) and loses to UCS. Report
    # that explicitly instead of leaving ids_equals_ucs to be misread.
    grid_ids = [r for r in out_rows if r["domain"] == "grid"]
    ids_solved = [r for r in grid_ids if r["ids_cost"] != ""]
    ids_eq_ucs = [r for r in ids_solved if r["ids_equals_ucs"] is True]
    ids_eq_bfs = [r for r in ids_solved if r["ids_cost"] == r["bfs_cost"]]
    print(f"  grid IDS: {len(ids_solved)}/{n_grid} solved "
          f"({n_grid - len(ids_solved)} timed out); it matched UCS on "
          f"{len(ids_eq_ucs)}/{len(ids_solved)} and matched BFS on "
          f"{len(ids_eq_bfs)}/{len(ids_solved)} — IDS returns the FEWEST-MOVE "
          f"path, so on non-uniform costs it is as suboptimal as BFS")

    _write("analysis1_optimality.csv", ANALYSIS1_FIELDS, out_rows)

    # The witness instance: the grid where BFS is *relatively* worst.
    if grid_bfs_worse:
        grid_bfs_worse.sort(reverse=True)
        rel, size, inst, row = grid_bfs_worse[0]
        grid = load_grids()[size][inst]
        bfs_path = _solve_grid_path(grid, "fifo")
        ucs_path = _solve_grid_path(grid, "ucs")
        lines = [
            "The instance where BFS is suboptimal (weighted grid, "
            "non-uniform costs)",
            f"size {size}x{size}, instance {inst} of the seeded bank",
            "terrain: '.' = 1, ',' = 3, '~' = 8;  S = start, G = goal",
            "",
            "  grid as given:",
        ]
        lines += ["  " + " ".join(grow) for grow in grid]
        lines += [
            "",
            f"  BFS (fewest moves) : {''.join(bfs_path)} -> cost {row['bfs_cost']}",
            f"  UCS (least cost)    : {''.join(ucs_path)} -> cost {row['ucs_cost']}",
            f"  A* + Manhattan      : cost {row['astar_manhattan']}",
            "",
            "  BFS counts MOVES, so it prefers the short-looking route through",
            f"  expensive terrain: +{row['bfs_cost'] - row['ucs_cost']} cost "
            f"({rel * 100:.1f}% over the optimum).",
            "",
        ]
        lines += render_grid_with_paths(grid, bfs_path, ucs_path,
                                        row["bfs_cost"], row["ucs_cost"])
        worst = RESULTS / "analysis1_bfs_worst_instance.txt"
        worst.write_text("\n".join(lines) + "\n")
        print(f"  worst BFS instance: {size}x{size} #{inst} — BFS cost "
              f"{row['bfs_cost']} vs UCS {row['ucs_cost']} "
              f"(+{row['bfs_cost'] - row['ucs_cost']}, {rel * 100:.1f}%)")
        print(f"  -> {worst}")

    # Minimal witness, straight from the studio: TinyGraph.
    tiny_bfs = s.bfs(TinyGraph("start", "A"))
    tiny_ucs = s.ucs(TinyGraph("start", "A"))
    print(f"  minimal witness (TinyGraph): BFS cost {tiny_bfs.cost} vs "
          f"UCS cost {tiny_ucs.cost}  (start->A costs 10, start->B->A costs 2)")
    return out_rows


def _solve_grid_path(grid, discipline):
    from engine import search as engine_search
    r = engine_search(GridProblem(grid), discipline)
    return list(r.node.path())


# ---- analysis 2: heuristic dominance ---------------------------------------

def analysis2(rows):
    print("\n=== Analysis 2 — heuristic dominance: Manhattan vs misplaced ===")
    per_instance = []
    violations = []
    for (size, inst), group in sorted(by_instance(rows, "puzzle").items()):
        if "A*+manhattan" not in group or "A*+misplaced" not in group:
            continue
        em = group["A*+manhattan"]["expansions"]
        ep = group["A*+misplaced"]["expansions"]
        ok = em <= ep
        if not ok:
            violations.append((size, inst, em, ep))
        per_instance.append({
            "size": size, "instance": inst,
            "expansions_misplaced": ep, "expansions_manhattan": em,
            "ratio_man_over_mis": f"{em / ep:.4f}" if ep else "",
            "manhattan_no_worse": ok,
        })
    _write("analysis2_dominance.csv",
           ["size", "instance", "expansions_misplaced", "expansions_manhattan",
            "ratio_man_over_mis", "manhattan_no_worse"], per_instance)

    # Pointwise, on states we can actually reach (seeded random walk).
    random.seed(20260807)
    checked = point_violations = 0
    for size, states in json.loads(
            (Path(__file__).with_name("instances_puzzle.json")).read_text()
    )["instances"].items():
        prob = EightPuzzle(tuple(states[0]))
        state = prob.initial
        for _ in range(400):
            state = prob.result(state, random.choice(prob.actions(state)))
            checked += 1
            if s.h_manhattan(prob, state) < s.h_misplaced(prob, state):
                point_violations += 1

    print(f"  expansions: A*+manhattan <= A*+misplaced on "
          f"{len(per_instance) - len(violations)}/{len(per_instance)} instances")
    print(f"  pointwise:  h_manhattan >= h_misplaced on {checked - point_violations}"
          f"/{checked} reachable states (seeded walk)")
    if violations:
        print(f"  VIOLATIONS: {violations} — a counterexample means a BUG in one "
              f"of the heuristics; do not report it as a finding.")
    else:
        print("  no counterexample — dominance holds on every instance measured")
    return per_instance


# ---- analysis 3: broken admissibility --------------------------------------

def analysis3(rows):
    print("\n=== Analysis 3 — break admissibility (h x 3): speedup AND cost ===")
    out_rows = []
    # h x 3 is what the spec asks for; the grid arm also carries the studio's
    # h_bad (x 8) as an extra, so both domains are measured with the same x 3.
    plans = [
        ("puzzle", "A*+manhattan", "A*+3xmanhattan", 3),
        ("grid", "A*+manhattan", "A*+3xmanhattan", 3),
        ("grid", "A*+manhattan", "A*+8xmanhattan", 8),
    ]
    for domain, good, bad, factor in plans:
        speed_exp, speed_time, gaps = [], [], []
        plan_rows = []
        n_sub = n = 0
        for (size, inst), group in sorted(by_instance(rows, domain).items()):
            if good not in group or bad not in group:
                continue
            g, b = group[good], group[bad]
            opt = group.get("UCS", {}).get("cost")
            if opt is None:
                continue
            n += 1
            gap = b["cost"] - opt
            if gap > 0:
                n_sub += 1
                gaps.append(gap)
            se = g["expansions"] / b["expansions"] if b["expansions"] else None
            st = g["seconds"] / b["seconds"] if b["seconds"] > 0 else None
            if se:
                speed_exp.append(se)
            if st:
                speed_time.append(st)
            out_row = {
                "domain": domain, "size": size, "instance": inst,
                "factor": factor,
                "optimal_cost": opt,
                "admissible_cost": g["cost"], "inadmissible_cost": b["cost"],
                "admissible_expansions": g["expansions"],
                "inadmissible_expansions": b["expansions"],
                "speedup_expansions": f"{se:.4f}" if se else "",
                "speedup_seconds": f"{st:.4f}" if st else "",
                "cost_gap_vs_optimum": gap,
                "length_gap": (b["length"] - g["length"]),
                "suboptimal": gap > 0,
            }
            plan_rows.append(out_row)
            out_rows.append(out_row)
        q1e, q3e = _iqr(speed_exp)
        q1t, q3t = _iqr(speed_time)
        extra = "  [extra beyond the spec's x 3]" if factor != 3 else ""
        print(f"  {domain}: h x {factor}  ({bad} vs {good}){extra}")
        print(f"    speedup in expansions : median {_med(speed_exp):.2f}x  "
              f"IQR [{q1e:.2f}, {q3e:.2f}]   (n={len(speed_exp)})")
        print(f"    speedup in wall-clock : median {_med(speed_time):.2f}x  "
              f"IQR [{q1t:.2f}, {q3t:.2f}]   (n={len(speed_time)})")
        print(f"    solution quality      : {n_sub}/{n} instances suboptimal; "
              f"cost gap median {_med(gaps) if gaps else 0:g}, "
              f"max {max(gaps) if gaps else 0:g} moves over optimum")
        if gaps:
            worst = max(plan_rows, key=lambda r: r["cost_gap_vs_optimum"])
            print(f"    worst case: {worst['domain']} {worst['size']} "
                  f"#{worst['instance']} — cost {worst['inadmissible_cost']} vs "
                  f"optimum {worst['optimal_cost']} "
                  f"(+{worst['cost_gap_vs_optimum']})")
    _write("analysis3_inadmissible.csv",
           ["domain", "size", "instance", "factor", "optimal_cost",
            "admissible_cost", "inadmissible_cost", "admissible_expansions",
            "inadmissible_expansions", "speedup_expansions", "speedup_seconds",
            "cost_gap_vs_optimum", "length_gap", "suboptimal"], out_rows)
    return out_rows


# ---- analysis 4: effective branching factor --------------------------------

def effective_bf(N, d, lo=1.0000001, hi=10.0, tol=1e-6):
    """Solve 1 + b + b^2 + ... + b^d = N + 1 for b, by bisection.

    Verbatim from the week-4 notebook (``effective_bf``): the branching factor a
    uniform tree of depth d would need in order to contain N nodes.
    """
    def total(b):
        return sum(b ** i for i in range(d + 1))
    for _ in range(200):
        mid = (lo + hi) / 2
        if total(mid) < N + 1:
            lo = mid
        else:
            hi = mid
        if hi - lo < tol:
            break
    return (lo + hi) / 2


def analysis4(rows):
    print("\n=== Analysis 4 — effective branching factor b* for A* ===")
    out_rows = []
    for domain in ("puzzle", "grid"):
        for size in SIZES[domain]:
            for algo in sorted({r["algorithm"] for r in rows
                                if r["domain"] == domain
                                and r["algorithm"].startswith("A*")}):
                sel = [r for r in rows if r["domain"] == domain
                       and r["size"] == size and r["algorithm"] == algo
                       and r["status"] == "solved"]
                if not sel:
                    continue
                bstars = [effective_bf(r["expansions"], r["length"]) for r in sel]
                out_rows.append({
                    "domain": domain, "size": size, "algorithm": algo,
                    "n": len(sel),
                    "expansions_median": int(_med([r["expansions"] for r in sel])),
                    "length_median": int(_med([r["length"] for r in sel])),
                    "bstar_median": f"{_med(bstars):.4f}",
                    "bstar_q1": f"{_iqr(bstars)[0]:.4f}",
                    "bstar_q3": f"{_iqr(bstars)[1]:.4f}",
                })
    _write("bstar.csv",
           ["domain", "size", "algorithm", "n", "expansions_median",
            "length_median", "bstar_median", "bstar_q1", "bstar_q3"], out_rows)

    for domain in ("puzzle", "grid"):
        print(f"  {domain}:")
        print(f"    {'depth':>6}  {'heuristic':<16}{'expansions':>10}{'b*':>8}")
        for r in out_rows:
            if r["domain"] != domain:
                continue
            print(f"    {r['size']:>6}  {r['algorithm']:<16}"
                  f"{r['expansions_median']:>10,}{r['bstar_median']:>8}")
    print("  b* near 1 = the search went almost straight to the goal; the")
    print("  question is whether it STAYS near 1 as depth grows.")
    return out_rows


def main():
    rows = load_rows()
    analysis1(rows)
    analysis2(rows)
    analysis3(rows)
    analysis4(rows)
    print("\nall four analyses written to", RESULTS)


if __name__ == "__main__":
    main()
