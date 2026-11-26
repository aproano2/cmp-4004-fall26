"""Brazo LLM (opción B) + estudio de hiperparámetros: PSO sobre Rastrigin D=10 (presupuesto 25 000).
Espacio de configuración común a LLM, random y grid: n (tamaño de enjambre, entero 5..100) y w (inercia, 0.1..1.0);
c1=c2=1.49618 fijos. Una 'configuración' = media del error final sobre las 5 semillas de entrenamiento 100..104."""
import json, numpy as np
from core import run_one

PROB, ALGO = "rastrigin_D10", "PSO_clerc"
TRAIN = list(range(100, 105))
TEST = list(range(200, 220))
NRANGE, WRANGE = (5, 100), (0.1, 1.0)
GRID_N, GRID_W = [10, 20, 40, 80], [0.3, 0.5, 0.7, 0.9]

def eval_config(n, w, seeds=TRAIN):
    n = int(round(min(max(n, NRANGE[0]), NRANGE[1])))
    w = float(min(max(w, WRANGE[0]), WRANGE[1]))
    finals, traces = [], []
    for s in seeds:
        tr, b, _ = run_one(PROB, ALGO, s, dict(n=n, w=w))
        finals.append(b); traces.append(tr)
    traces = np.array(traces)
    cap = traces.shape[1]
    at = {f"{int(p*100)}%": float(np.mean(traces[:, int(p * cap) - 1])) for p in (0.04, 0.1, 0.25, 0.5, 1.0)}
    return dict(n=n, w=w, finals=[float(x) for x in finals], mean=float(np.mean(finals)),
                median=float(np.median(finals)), std=float(np.std(finals)), mean_best_at_budget_fraction=at)

def feedback_text(results, start_idx):
    lines = []
    for k, r in enumerate(results):
        a = r["mean_best_at_budget_fraction"]
        lines.append(f"config #{start_idx + k}: n={r['n']}, w={r['w']:.3f} -> mean_final={r['mean']:.3f} "
                     f"(median {r['median']:.3f}, std {r['std']:.3f}, per-seed {[round(x,2) for x in r['finals']]}); "
                     f"mean best-so-far at 4%/10%/25%/50%/100% of budget = "
                     + "/".join(f"{a[k2]:.2f}" for k2 in ("4%", "10%", "25%", "50%", "100%")))
    return "\n".join(lines)
