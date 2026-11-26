"""Estudio de hiperparámetros (grid n x w, 5 seeds) + comparación LLM vs random vs grid (mismas 16 configuraciones)."""
import json, numpy as np, pandas as pd
from tuning import *
rng = np.random.default_rng(12345)
C = "../.llm_cache"

# ---- grid (sirve a la vez de estudio de hiperparámetros y de grid search de 16 configs)
grid = []
for n in GRID_N:
    for w in GRID_W:
        r = eval_config(n, w)
        for s, v in zip(TRAIN, r["finals"]):
            grid.append(dict(n=n, w=w, seed=s, final=v))
pd.DataFrame(grid).to_csv("../results/hyperparam_grid_pso.csv", index=False)
gdf = pd.DataFrame(grid).groupby(["n", "w"]).final.mean().reset_index()
g_best = gdf.loc[gdf.final.idxmin()]

# ---- LLM
llm = []
idx = 0
for k in range(1, 5):
    for r in json.load(open(f"{C}/round{k}_results.json"))["results"]:
        idx += 1
        for s, v in zip(TRAIN, r["finals"]):
            llm.append(dict(method="LLM", draw=0, idx=idx, round=k, n=r["n"], w=r["w"], seed=s, final=v))
ldf = pd.DataFrame(llm)
l_means = ldf.groupby(["idx", "n", "w"]).final.mean().reset_index().sort_values("idx")
l_best = l_means.loc[l_means.final.idxmin()]

# ---- random search sobre configuraciones: 30 repeticiones independientes de 16 configs
rnd = []
r_best = []
for d in range(30):
    for i in range(1, 17):
        n = int(rng.integers(NRANGE[0], NRANGE[1] + 1)); w = float(rng.uniform(*WRANGE))
        r = eval_config(n, w)
        for s, v in zip(TRAIN, r["finals"]):
            rnd.append(dict(method="Random", draw=d, idx=i, round=0, n=n, w=w, seed=s, final=v))
rdf = pd.DataFrame(rnd)
trials = pd.concat([ldf, rdf, pd.DataFrame(grid).assign(method="Grid", draw=0, idx=lambda x: (x.index // 5) + 1, round=0)])
trials.to_csv("../results/tuning_trials.csv", index=False)
rm = rdf.groupby(["draw", "idx", "n", "w"]).final.mean().reset_index()
for d in range(30):
    sub = rm[rm.draw == d]
    r_best.append(sub.loc[sub.final.idxmin()])

# ---- trayectoria best-so-far (tras cada config) sobre la media de entrenamiento
traj = []
for i, row in enumerate(l_means.itertuples(), 1):
    traj.append(dict(method="LLM", draw=0, idx=i, best_so_far=l_means.final.iloc[:i].min()))
for d in range(30):
    sub = rm[rm.draw == d].sort_values("idx")
    for i in range(1, 17):
        traj.append(dict(method="Random", draw=d, idx=i, best_so_far=sub.final.iloc[:i].min()))
gm = pd.DataFrame(grid).groupby(["n", "w"], sort=False).final.mean().values  # orden n-mayor, w-menor
for i in range(1, 17):
    traj.append(dict(method="Grid", draw=0, idx=i, best_so_far=gm[:i].min()))
pd.DataFrame(traj).to_csv("../results/tuning_trajectories.csv", index=False)

# ---- evaluación en seeds de TEST (no vistas) de la config elegida por cada método
test = []
def run_test(label, draw, n, w, train_mean):
    r = eval_config(n, w, TEST)
    for s, v in zip(TEST, r["finals"]):
        test.append(dict(method=label, draw=draw, n=r["n"], w=r["w"], train_mean=train_mean, seed=s, final=v))
run_test("Default (n=40,w=0.7298)", 0, 40, 0.7298, np.nan)
run_test("Grid", 0, g_best.n, g_best.w, g_best.final)
run_test("LLM", 0, l_best.n, l_best.w, l_best.final)
for d, row in enumerate(r_best):
    run_test("Random", d, row.n, row.w, row.final)
pd.DataFrame(test).to_csv("../results/tuning_test.csv", index=False)
print("grid best", dict(g_best), "\nllm best", dict(l_best))
print(gdf.pivot(index="n", columns="w", values="final").round(2))
print("random-best train mean: median", np.median([r.final for r in r_best]).round(2))
t = pd.DataFrame(test)
print(t.groupby(["method"]).final.agg(["mean", "median", "std"]).round(2))
