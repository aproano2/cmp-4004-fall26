"""Tablas, scorecard y figuras a partir de results/*.csv"""
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import mannwhitneyu
R, F = "../results/", "../fig/"
fin = pd.read_csv(R + "main_final.csv"); conv = pd.read_csv(R + "main_convergence.csv")
INK, MUTED, GRID, BG = "#0b0b0b", "#898781", "#e1e0d9", "#fcfcfb"
COL = {"RS": "#898781", "HC": "#0b0b0b", "NN2OPT": "#0b0b0b", "GA": "#2a78d6", "SA": "#eb6834", "PSO": "#1baf7a",
       "PSO_clerc": "#008300", "ABC": "#e87ba4", "ABC_T": "#e87ba4", "ACO": "#6250d6", "ACO_b0": "#e34948", "ACO_MMAS": "#eda100"}
LS = {"RS": ":", "HC": "--", "NN2OPT": "--", "ACO_b0": "-.", "PSO_clerc": "--", "ACO_MMAS": "--"}
LAB = {"RS": "Random search", "HC": "Hill climb + reinicios", "NN2OPT": "NN + 2-opt (ILS)", "GA": "GA (propio)", "SA": "SA (propio)",
       "PSO": "PSO (oficial)", "PSO_clerc": "PSO-Clerc (propio)", "ABC": "ABC (oficial)", "ABC_T": "ABC perm. (propio)",
       "ACO": "ACO (oficial)", "ACO_b0": "ACO oficial β=0", "ACO_MMAS": "ACO-MMAS (propio)"}
plt.rcParams.update({"figure.facecolor": BG, "axes.facecolor": BG, "axes.edgecolor": "#c3c2b7", "axes.labelcolor": INK,
                     "xtick.color": MUTED, "ytick.color": MUTED, "text.color": INK, "axes.grid": True, "grid.color": GRID,
                     "grid.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False, "font.size": 9,
                     "savefig.dpi": 150, "savefig.facecolor": BG})
PROBS = list(dict.fromkeys(fin.problem))
HEUR = {"continuous": "HC", "tsp": "NN2OPT"}

# ---------------- tablas
rows = []
for p in PROBS:
    d = fin[fin.problem == p]; rs = d[d.algo == "RS"].final.values
    for a, g in d.groupby("algo"):
        v = g.final.values
        pv = np.nan if a == "RS" else mannwhitneyu(v, rs, alternative="less").pvalue
        rows.append(dict(problem=p, algo=a, n_seeds=len(v), budget=int(g.budget.iloc[0]), mean=v.mean(), std=v.std(ddof=1),
                         median=np.median(v), q1=np.percentile(v, 25), q3=np.percentile(v, 75), min=v.min(), p_vs_RS=pv,
                         seconds=g.seconds.mean()))
S = pd.DataFrame(rows)
S["rank"] = S.groupby("problem")["median"].rank(method="min")
S.to_csv(R + "summary_table.csv", index=False)

# ---------------- scorecard
sc = []
for p in PROBS:
    s = S[S.problem == p].sort_values("median"); kind = "tsp" if p.startswith("tsp") else "continuous"
    best = s.iloc[0]; rsr = s[s.algo == "RS"].iloc[0]; h = s[s.algo == HEUR[kind]].iloc[0]
    meta = s[~s.algo.isin(["RS", HEUR[kind], "ACO_b0"])]
    bm = meta.iloc[0]
    d = fin[fin.problem == p]
    # ¿el mejor meta vence al baseline específico? (MWU unilateral)
    pv_h = mannwhitneyu(d[d.algo == bm.algo].final, d[d.algo == HEUR[kind]].final, alternative="less").pvalue
    sc.append(dict(problem=p, budget=int(best.budget), winner=best.algo, winner_median=best["median"],
                   best_metaheuristic=bm.algo, bm_median=bm["median"], heuristic_median=h["median"],
                   rs_median=rsr["median"], bm_beats_RS_p=bm.p_vs_RS, bm_beats_heuristic_p=pv_h,
                   rs_rank=int(rsr["rank"]), n_algos=len(s)))
SC = pd.DataFrame(sc); SC.to_csv(R + "scorecard.csv", index=False)

def fmt(x):
    return f"{x:.3g}" if abs(x) < 1e3 else f"{x:.0f}"
with open(R + "summary_tables.md", "w") as f:
    for p in PROBS:
        s = S[S.problem == p].sort_values("median")
        f.write(f"\n**{p}** (presupuesto {int(s.budget.iloc[0])} evals, {int(s.n_seeds.iloc[0])} seeds)\n\n| Algoritmo | media ± std | mediana [Q1–Q3] | p vs RS |\n|---|---|---|---|\n")
        for r in s.itertuples():
            pv = "—" if np.isnan(r.p_vs_RS) else (f"{r.p_vs_RS:.1e}")
            f.write(f"| {LAB[r.algo]} | {fmt(r.mean)} ± {fmt(r.std)} | {fmt(r.median)} [{fmt(r.q1)}–{fmt(r.q3)}] | {pv} |\n")
print(SC.to_string())

# ---------------- convergencia
def conv_fig(probs, fname, title, logy):
    fig, axs = plt.subplots(1, len(probs), figsize=(4.6 * len(probs), 3.9))
    for ax, p in zip(np.atleast_1d(axs), probs):
        kind = "tsp" if p.startswith("tsp") else "continuous"
        d = conv[conv.problem == p]
        for a in [x for x in LAB if x in set(d.algo)]:
            q = d[d.algo == a].groupby("evals").best_so_far.quantile([.25, .5, .75]).unstack()
            lo, md, hi = [np.maximum(q[k], 1e-10) if logy else q[k] for k in (.25, .5, .75)]
            ax.plot(q.index, md, color=COL[a], ls=LS.get(a, "-"), lw=1.8 if a not in ("RS",) else 1.4, label=LAB[a])
            ax.fill_between(q.index, lo, hi, color=COL[a], alpha=0.15, lw=0)
        ax.set_xscale("log")
        if logy: ax.set_yscale("log")
        ax.set_xlabel("evaluaciones de la función objetivo"); ax.set_title(p.replace("_", " "), fontsize=10, loc="left")
        cap = int(fin[fin.problem == p].budget.iloc[0]); ax.axvline(cap, color=MUTED, lw=0.8)
    np.atleast_1d(axs)[0].set_ylabel("mejor valor hallado (mediana, banda = IQR, 20 seeds)")
    h, l = np.atleast_1d(axs)[-1].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=min(len(l), 5), frameon=False, fontsize=8)
    fig.suptitle(title, x=0.01, ha="left", fontsize=11)
    fig.tight_layout(rect=(0, 0.1, 1, 0.95)); fig.savefig(F + fname); plt.close(fig)
conv_fig([p for p in PROBS if p.startswith("rastrigin")], "conv_rastrigin.png", "Rastrigin: convergencia vs evaluaciones", True)
conv_fig([p for p in PROBS if p.startswith("rosenbrock")], "conv_rosenbrock.png", "Rosenbrock: convergencia vs evaluaciones", True)
conv_fig([p for p in PROBS if p.startswith("tsp")], "conv_tsp.png", "TSP: longitud de tour vs evaluaciones", False)

# ---------------- boxplot final por problema
fig, axs = plt.subplots(3, 3, figsize=(12, 9))
for ax, p in zip(axs.ravel(), PROBS):
    d = fin[fin.problem == p]; order = list(S[S.problem == p].sort_values("median").algo)
    bp = ax.boxplot([d[d.algo == a].final for a in order], vert=False, patch_artist=True, widths=0.6,
                    medianprops=dict(color=INK, lw=1.5), flierprops=dict(markersize=3, markeredgecolor=MUTED))
    for b, a in zip(bp["boxes"], order): b.set_facecolor(COL[a]); b.set_alpha(0.55); b.set_edgecolor(COL[a])
    ax.set_yticks(range(1, len(order) + 1)); ax.set_yticklabels([LAB[a].split(" (")[0] for a in order], fontsize=7)
    ax.invert_yaxis(); ax.set_title(p.replace("_", " "), fontsize=9, loc="left")
    if not p.startswith("tsp"): ax.set_xscale("symlog", linthresh=1e-3)
fig.suptitle("Valor final por algoritmo (20 seeds, presupuesto idéntico; menor = mejor)", x=0.01, ha="left")
fig.tight_layout(rect=(0, 0, 1, 0.97)); fig.savefig(F + "final_boxplots.png"); plt.close(fig)

# ---------------- heatmap hiperparámetros
g = pd.read_csv(R + "hyperparam_grid_pso.csv")
m = g.groupby(["n", "w"]).final.mean().unstack(); sd = g.groupby(["n", "w"]).final.std().unstack()
fig, ax = plt.subplots(figsize=(5.4, 4.2))
im = ax.imshow(m.values, cmap="Blues_r", aspect="auto")
ax.set_xticks(range(len(m.columns))); ax.set_xticklabels(m.columns); ax.set_yticks(range(len(m.index))); ax.set_yticklabels(m.index)
ax.set_xlabel("inercia w"); ax.set_ylabel("tamaño del enjambre n"); ax.grid(False)
for i in range(m.shape[0]):
    for j in range(m.shape[1]):
        ax.text(j, i, f"{m.values[i,j]:.1f}\n±{sd.values[i,j]:.1f}", ha="center", va="center", fontsize=8,
                color="white" if m.values[i, j] < np.median(m.values) else INK)
fig.colorbar(im, label="error final medio (5 seeds)"); ax.set_title("PSO en Rastrigin D=10: n × w", loc="left", fontsize=10)
fig.tight_layout(); fig.savefig(F + "heatmap_pso.png"); plt.close(fig)

# ---------------- tuning LLM vs random vs grid
tr = pd.read_csv(R + "tuning_trajectories.csv"); te = pd.read_csv(R + "tuning_test.csv")
fig, axs = plt.subplots(1, 2, figsize=(10, 3.8))
ax = axs[0]
q = tr[tr.method == "Random"].groupby("idx").best_so_far.quantile([.1, .5, .9]).unstack()
ax.plot(q.index, q[.5], color="#898781", ls=":", lw=1.6, label="Random (mediana, 30 repeticiones)"); ax.fill_between(q.index, q[.1], q[.9], color="#898781", alpha=.18, lw=0)
for mth, c, ls in (("Grid", "#eb6834", "--"), ("LLM", "#2a78d6", "-")):
    t = tr[tr.method == mth]; ax.plot(t.idx, t.best_so_far, color=c, ls=ls, lw=2, marker="o", ms=4, label=mth + (" (1 trayectoria)" if mth == "LLM" else " 4×4"))
ax.set_xlabel("nº de configuraciones evaluadas"); ax.set_ylabel("mejor error medio en seeds de entrenamiento"); ax.set_title("Entrenamiento (seeds 100–104)", loc="left", fontsize=10); ax.legend(frameon=False, fontsize=8)
ax = axs[1]
order = ["Default (n=40,w=0.7298)", "Grid", "LLM", "Random"]
rnd_means = te[te.method == "Random"].groupby("draw").final.mean()
ax.boxplot([te[te.method == "Default (n=40,w=0.7298)"].final, te[te.method == "Grid"].final, te[te.method == "LLM"].final, te[te.method == "Random"].groupby("draw").final.mean()],
           tick_labels=["Default", "Grid", "LLM", "Random\n(media/repetición)"], patch_artist=True, medianprops=dict(color=INK))
ax.set_ylabel("error final (seeds de TEST 200–219)"); ax.set_title("Config elegida, evaluada en seeds no vistas", loc="left", fontsize=10)
fig.tight_layout(); fig.savefig(F + "tuning_llm_random_grid.png"); plt.close(fig)

# ---------------- stats de tuner para el reporte
L = te[te.method == "LLM"].final; Gt = te[te.method == "Grid"].final; D = te[te.method == "Default (n=40,w=0.7298)"].final
print("LLM test mean", L.mean(), "grid", Gt.mean(), "default", D.mean(), "random mean-of-means", rnd_means.mean(),
      "frac random draws better than LLM:", (rnd_means < L.mean()).mean(), "LLM vs default MWU p", mannwhitneyu(L, D, alternative="less").pvalue)
print("random-draw train best median", tr[(tr.method=="Random")&(tr.idx==16)].best_so_far.median(), "LLM train", tr[(tr.method=="LLM")&(tr.idx==16)].best_so_far.iloc[0], "Grid train", tr[(tr.method=="Grid")&(tr.idx==16)].best_so_far.iloc[0])
print(te.groupby("method").train_mean.first())
