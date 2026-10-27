"""Parte 1 - comparación clásica. Se corre desde la carpeta del deber:

    python code/benchmark.py

Escribe en results/:
    classical_runs.csv      una fila por (instancia, algoritmo)  <- datos crudos
    classical_summary.csv   mediana + IQR por (dominio, nivel, algoritmo)
    optimality_check.csv    costo de UCS vs A* vs BFS en cada instancia     (análisis 1)
    dominance.csv           expansiones misplaced vs Manhattan por puzzle   (análisis 2)
    weighted_astar.csv      h vs 3h: expansiones, tiempo y costo            (análisis 3)
    ebf.csv                 factor de ramificación efectivo por instancia   (análisis 4)
"""
import csv
import platform
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from domains import (all_instances, make_problem, h_misplaced,             # noqa: E402
                     h_manhattan_puzzle, h_manhattan_grid)
from search import (bfs, dfs, ucs, ids, astar, TIMEOUT_S,                  # noqa: E402
                    effective_branching_factor)

RESULTS = Path(__file__).resolve().parent.parent / "results"

ALGORITHMS = {
    "puzzle": [
        ("BFS", bfs), ("DFS", dfs), ("UCS", ucs), ("IDS", ids),
        ("A*-misplaced", lambda p: astar(p, h_misplaced, name="A*-misplaced")),
        ("A*-manhattan", lambda p: astar(p, h_manhattan_puzzle, name="A*-manhattan")),
        ("A*-3xmanhattan", lambda p: astar(p, h_manhattan_puzzle, weight=3,
                                           name="A*-3xmanhattan")),
    ],
    "grid": [
        ("BFS", bfs), ("DFS", dfs), ("UCS", ucs), ("IDS", ids),
        ("A*-manhattan", lambda p: astar(p, h_manhattan_grid, name="A*-manhattan")),
        ("A*-3xmanhattan", lambda p: astar(p, h_manhattan_grid, weight=3,
                                           name="A*-3xmanhattan")),
    ],
}
METRICS = ["cost", "length", "expansions", "max_frontier", "time_s"]


def write_csv(name, rows):
    RESULTS.mkdir(exist_ok=True)
    with open(RESULTS / name, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"  escrito results/{name} ({len(rows)} filas)")


def run_all():
    rows = []
    for domain, level, idx, inst in all_instances():
        problem = make_problem(domain, inst)
        for name, algo in ALGORITHMS[domain]:
            r = algo(problem)
            rows.append({
                "domain": domain, "level": level, "instance": idx,
                "algorithm": name, "status": r.status,
                "cost": r.cost if r.solved else "",
                "length": r.length if r.solved else "",
                "expansions": r.expansions, "generated": r.generated,
                "max_frontier": r.max_frontier, "time_s": f"{r.time_s:.6f}",
            })
        print(f"  {domain} nivel {level} instancia {idx} listo", flush=True)
    return rows


def summarize(rows):
    """Mediana y cuartiles sobre las corridas RESUELTAS; los timeouts se cuentan aparte."""
    groups = {}
    for r in rows:
        groups.setdefault((r["domain"], r["level"], r["algorithm"]), []).append(r)
    out = []
    for (domain, level, algo), rs in groups.items():
        solved = [r for r in rs if r["status"] == "solved"]
        row = {"domain": domain, "level": level, "algorithm": algo, "n": len(rs),
               "n_solved": len(solved),
               "n_timeout": sum(r["status"] == "timeout" for r in rs)}
        for m in METRICS:
            vals = [float(r[m]) for r in solved]
            if vals:
                q1, med, q3 = np.percentile(vals, [25, 50, 75])
                row.update({f"{m}_median": round(med, 6), f"{m}_q1": round(q1, 6),
                            f"{m}_q3": round(q3, 6), f"{m}_iqr": round(q3 - q1, 6)})
            else:
                row.update({f"{m}_median": "", f"{m}_q1": "", f"{m}_q3": "",
                            f"{m}_iqr": ""})
        out.append(row)
    return out


def index(rows):
    return {(r["domain"], r["level"], r["instance"], r["algorithm"]): r for r in rows}


def analyses(rows):
    by = index(rows)
    instances = sorted({(r["domain"], r["level"], r["instance"]) for r in rows})

    # 1. UCS == A* en costo; BFS no es óptimo cuando los costos no son uniformes
    opt = []
    for d, lv, i in instances:
        u, a, b = (by[d, lv, i, n] for n in ("UCS", "A*-manhattan", "BFS"))
        opt.append({"domain": d, "level": lv, "instance": i,
                    "ucs_cost": u["cost"], "astar_cost": a["cost"],
                    "bfs_cost": b["cost"], "bfs_length": b["length"],
                    "astar_length": a["length"],
                    "ucs_equals_astar": u["cost"] == a["cost"],
                    "bfs_suboptimal": b["cost"] > a["cost"]})
    write_csv("optimality_check.csv", opt)

    # 2. dominancia de heurísticas en el 8-puzzle
    dom = []
    for d, lv, i in instances:
        if d != "puzzle":
            continue
        mis, man = by[d, lv, i, "A*-misplaced"], by[d, lv, i, "A*-manhattan"]
        dom.append({"level": lv, "instance": i,
                    "expansions_misplaced": mis["expansions"],
                    "expansions_manhattan": man["expansions"],
                    "manhattan_le_misplaced": man["expansions"] <= mis["expansions"]})
    write_csv("dominance.csv", dom)

    # 3. h admisible vs 3h
    wa = []
    for d, lv, i in instances:
        a, w = by[d, lv, i, "A*-manhattan"], by[d, lv, i, "A*-3xmanhattan"]
        wa.append({"domain": d, "level": lv, "instance": i,
                   "expansions_h": a["expansions"], "expansions_3h": w["expansions"],
                   "expansion_speedup": round(a["expansions"] / max(w["expansions"], 1), 3),
                   "time_h": a["time_s"], "time_3h": w["time_s"],
                   "time_speedup": round(float(a["time_s"]) / float(w["time_s"]), 3),
                   "cost_h": a["cost"], "cost_3h": w["cost"],
                   "cost_ratio": round(w["cost"] / a["cost"], 4),
                   "suboptimal": w["cost"] > a["cost"]})
    write_csv("weighted_astar.csv", wa)

    # 4. factor de ramificación efectivo (N = nodos generados, d = longitud de la solución)
    ebf = []
    for d, lv, i in instances:
        for name in [n for n, _ in ALGORITHMS[d] if n.startswith("A*")]:
            r = by[d, lv, i, name]
            ebf.append({"domain": d, "level": lv, "instance": i, "heuristic": name,
                        "generated": r["generated"], "depth": r["length"],
                        "b_star": round(effective_branching_factor(
                            r["generated"], r["length"]), 4)})
    write_csv("ebf.csv", ebf)


if __name__ == "__main__":
    print(f"Timeout por corrida: {TIMEOUT_S} s | Python {platform.python_version()} "
          f"| {platform.platform()}")
    rows = run_all()
    write_csv("classical_runs.csv", rows)
    write_csv("classical_summary.csv", summarize(rows))
    analyses(rows)
