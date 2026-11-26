"""Experimento principal: todos los algoritmos x problemas x 20 seeds, presupuesto idéntico por problema."""
import numpy as np, pandas as pd, itertools, time
from multiprocessing import Pool
from core import run_one, make_problem
from algorithms import SETS

SEEDS = list(range(20))
PROBLEMS = [f"{f}_D{d}" for f in ("rastrigin", "rosenbrock") for d in (2, 10, 30)] + [f"tsp_{n}" for n in (20, 30, 50)]

def job(a):
    key, algo, seed = a
    tr, best, dt = run_one(key, algo, seed)
    cap = len(tr)
    cps = np.unique(np.round(np.logspace(0, np.log10(cap), 100)).astype(int)) - 1
    return key, algo, seed, cap, best, dt, cps, tr[cps]

if __name__ == "__main__":
    jobs = [(k, a, s) for k in PROBLEMS for a in SETS["tsp" if k.startswith("tsp") else "continuous"] for s in SEEDS]
    t0 = time.time()
    fin, conv = [], []
    with Pool(2) as p:
        for key, algo, seed, cap, best, dt, cps, vals in p.imap_unordered(job, jobs, chunksize=4):
            fin.append(dict(problem=key, algo=algo, seed=seed, budget=cap, evals_used=cap, final=best, seconds=dt))
            conv += [(key, algo, seed, int(e) + 1, float(v)) for e, v in zip(cps, vals)]
    pd.DataFrame(fin).sort_values(["problem", "algo", "seed"]).to_csv("../results/main_final.csv", index=False)
    pd.DataFrame(conv, columns=["problem", "algo", "seed", "evals", "best_so_far"]).to_csv("../results/main_convergence.csv", index=False)
    print("done", len(jobs), "runs in", round(time.time() - t0), "s")
