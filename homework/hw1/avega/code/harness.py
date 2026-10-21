"""The Part 1 benchmark harness — runs the protocol, writes the raw CSVs.

Protocol (from ``hw-1-search.md``):

  * two domains: 8-puzzle (uniform cost) and weighted grid (terrain 1/3/8);
  * four difficulty levels each — puzzle solution depths 4/8/12/16, grids
    5x5/8x8/12x12/16x16 — **ten instances per level** (both banks are the seeded
    studio banks, seed 20260807, 40 + 40 instances);
  * per algorithm per domain: solution cost, solution length, node expansions,
    maximum frontier size, wall-clock time;
  * a hard timeout of 120 s per instance, reported as ``timeout`` — never as a
    failure to solve;
  * medians and IQRs, never a single run.

Usage::

    python3 harness.py                  # everything (resumable)
    python3 harness.py --domain puzzle  # one domain
    python3 harness.py --fresh          # discard previous raw CSVs first
    python3 harness.py --timeout 120

Rows are appended and flushed as they arrive, so an interrupted run resumes
where it stopped (``--fresh`` starts over). Known slow cell: IDS on grids is a
tree search with no transposition table — 16x16 times out on purpose.
"""

from __future__ import annotations

import argparse
import csv
import statistics
import sys
import time
from pathlib import Path

from gridworld import GridProblem, load_instances as load_grids
from search import EightPuzzle
from search import load_instances as load_puzzles

import starter as s

ROOT = Path(__file__).resolve().parent.parent          # .../hw1/<team>/
RESULTS = ROOT / "results"
TIMEOUT_DEFAULT = 120.0

FIELDS = ["domain", "size", "instance", "algorithm", "status", "cost", "length",
          "expansions", "generated", "max_frontier", "seconds"]

DOMAINS = {
    "puzzle": {
        "sizes": [4, 8, 12, 16],
        "levels": "solution depth",
        # NB: search.load_instances() defaults to "instances.json" NEXT TO IT —
        # which here is the *grid* bank. The puzzle bank is always passed
        # explicitly as instances_puzzle.json.
        "problems": lambda: {size: [EightPuzzle(st) for st in states]
                             for size, states in load_puzzles(
                                 Path(__file__).with_name("instances_puzzle.json")
                             ).items()},
    },
    "grid": {
        "sizes": [5, 8, 12, 16],
        "levels": "grid size",
        "problems": lambda: {size: [GridProblem(g) for g in grids]
                             for size, grids in load_grids().items()},
    },
}


# ---- running ----------------------------------------------------------------

def run_domain(domain: str, timeout: float, fresh: bool) -> Path:
    out = RESULTS / f"raw_{domain}.csv"
    RESULTS.mkdir(exist_ok=True)
    if fresh and out.exists():
        out.unlink()

    done = set()
    if out.exists():
        with out.open(newline="") as fh:
            for row in csv.DictReader(fh):
                done.add((row["domain"], int(row["size"]), int(row["instance"]),
                          row["algorithm"]))

    bank = DOMAINS[domain]["problems"]()
    algos = s.algorithms(domain)
    t0 = time.perf_counter()
    new = 0
    write_header = not out.exists() or out.stat().st_size == 0
    with out.open("a", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        if write_header:
            writer.writeheader()
        for size in DOMAINS[domain]["sizes"]:
            for i, prob in enumerate(bank[size]):
                for name, algo in algos:
                    if (domain, size, i, name) in done:
                        continue
                    # Same hard deadline for every algorithm. IDS treats it as
                    # a *total* budget across its deepening iterations; the
                    # other four check it once per expansion.
                    r = algo(prob, timeout=timeout)
                    row = {
                        "domain": domain, "size": size, "instance": i,
                        "algorithm": name, "status": r.status,
                        "cost": "" if r.cost is None else r.cost,
                        "length": "" if r.length is None else r.length,
                        "expansions": r.expansions, "generated": r.generated,
                        "max_frontier": r.max_frontier,
                        "seconds": f"{r.seconds:.6f}",
                    }
                    writer.writerow(row)
                    fh.flush()
                    new += 1
                    flag = "" if r.status == "solved" else f"   <-- {r.status.upper()}"
                    print(f"  {domain:<6} {DOMAINS[domain]['levels']} {size:>2}  "
                          f"inst {i:>2}  {name:<15} {r.status:<9} "
                          f"cost={str(r.cost):>6} len={str(r.length):>5} "
                          f"exp={r.expansions:>9,} maxF={r.max_frontier:>8,} "
                          f"{r.seconds:>7.3f}s{flag}", flush=True)
    print(f"[{domain}] {new} new rows -> {out} "
          f"({time.perf_counter() - t0:.1f}s wall)\n")
    return out


# ---- summarising ------------------------------------------------------------

def _median_iqr(values):
    """(median, q1, q3) over solved runs. Blank when there is nothing to
    summarise — a size where every run timed out is reported as such, not as
    a zero."""
    if not values:
        return "", "", ""
    if len(values) == 1:
        v = values[0]
        return f"{v:.6g}", f"{v:.6g}", f"{v:.6g}"
    q1, _, q3 = statistics.quantiles(values, n=4, method="inclusive")
    return f"{statistics.median(values):.6g}", f"{q1:.6g}", f"{q3:.6g}"


def summarize() -> Path:
    """Median + IQR per (domain, size, algorithm), over SOLVED runs only, with
    the timeout count kept next to them (timeouts are timeouts)."""
    out = RESULTS / "summary.csv"
    metrics = ["cost", "length", "expansions", "max_frontier", "seconds"]
    fields = ["domain", "size", "algorithm", "n_total", "n_solved", "n_timeout",
              "n_exhausted"]
    for m in metrics:
        fields += [f"{m}_median", f"{m}_q1", f"{m}_q3"]

    rows = []
    for domain in DOMAINS:
        path = RESULTS / f"raw_{domain}.csv"
        if not path.exists():
            continue
        with path.open(newline="") as fh:
            rows += list(csv.DictReader(fh))

    groups: dict[tuple, list[dict]] = {}
    for row in rows:
        groups.setdefault((row["domain"], int(row["size"]), row["algorithm"]),
                          []).append(row)

    with out.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for key in sorted(groups, key=lambda k: (k[0], k[1], k[2])):
            domain, size, algo = key
            group = groups[key]
            solved = [r for r in group if r["status"] == "solved"]
            line = {
                "domain": domain, "size": size, "algorithm": algo,
                "n_total": len(group),
                "n_solved": len(solved),
                "n_timeout": sum(r["status"] == "timeout" for r in group),
                "n_exhausted": sum(r["status"] == "exhausted" for r in group),
            }
            for m in metrics:
                med, q1, q3 = _median_iqr([float(r[m]) for r in solved])
                line[f"{m}_median"], line[f"{m}_q1"], line[f"{m}_q3"] = med, q1, q3
            w.writerow(line)
    print(f"summary -> {out}  ({len(groups)} groups)")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--domain", choices=["puzzle", "grid", "both"], default="both")
    ap.add_argument("--timeout", type=float, default=TIMEOUT_DEFAULT,
                    help="hard per-instance wall-clock budget in seconds "
                         "(default 120; IDS gets it as a total budget)")
    ap.add_argument("--fresh", action="store_true", help="discard existing rows")
    ap.add_argument("--no-summary", action="store_true")
    args = ap.parse_args()

    print(f"timeout = {args.timeout:g}s per instance")
    domains = ["puzzle", "grid"] if args.domain == "both" else [args.domain]
    for d in domains:
        run_domain(d, args.timeout, args.fresh)
    if not args.no_summary:
        summarize()


if __name__ == "__main__":
    main()
