"""Control de separabilidad: Rastrigin rotada (no separable) D=10 y D=30, mismos algoritmos/presupuesto/seeds."""
import pandas as pd
from multiprocessing import Pool
from core import run_one
from algorithms import SETS
def job(a):
    k, al, s = a; tr, b, dt = run_one(k, al, s); return dict(problem=k, algo=al, seed=s, budget=len(tr), evals_used=len(tr), final=b, seconds=dt)
if __name__ == "__main__":
    jobs = [(k, a, s) for k in ("rotrastrigin_D10", "rotrastrigin_D30") for a in SETS["continuous"] for s in range(20)]
    with Pool(2) as p: out = p.map(job, jobs, chunksize=4)
    df = pd.DataFrame(out); df.to_csv("../results/extra_rotated_rastrigin_final.csv", index=False)
    print(df.groupby(["problem", "algo"]).final.agg(["mean", "std", "median"]).round(3))
