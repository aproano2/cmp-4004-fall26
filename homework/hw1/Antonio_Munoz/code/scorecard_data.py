"""scorecard_data.py -- the numbers for the Duel Scorecard (classical / LLM / tool).
Reads ../results/*.csv, writes ../results/scorecard_data.csv and prints a summary.
Run: python3 scorecard_data.py"""
from pathlib import Path

import pandas as pd

import engine
import gridworld as GW
import heuristics_grid as HG

HERE = Path(__file__).parent
RES = HERE.parent / "results"
rows = []


def add(axis, system, value):
    rows.append({"axis": axis, "system": system, "value": value})


def med(x): return round(float(pd.Series(x).median()), 3)
def p95(x): return round(float(pd.Series(x).quantile(0.95)), 3)


# ---------------- classical A* (Manhattan) on the 40 grids ----------------
c = pd.read_csv(RES / "classical_grid.csv")
a = c[c.algo == "astar_manhattan"]
ucs = c[c.algo == "ucs"].set_index(["level", "instance"]).cost
k = sum(int(r.cost == ucs[(r.level, r.instance)]) for r in a.itertuples())
add("1 correctness", "classical", f"{k}/{len(a)} optimal (cost == UCS)")
add("3 cost", "classical", f"{med(a.expansions)} expansions (median)")
add("4 latency", "classical", f"{a.time_s.median() * 1000:.2f} ms median / "
    f"{a.time_s.quantile(0.95) * 1000:.2f} ms p95")
grid = GW.load_instances(HERE / "instances_grid.json")[8][0]
runs = [engine.run(GW.GridProblem(grid), "astar", HG.h_manhattan_scaled) for _ in range(5)]
d = len({("".join(r["path"]), r["cost"]) for r in runs})
add("5 reproducibility", "classical", f"{d} distinct answer(s) in 5 runs (grid 8x8 #0)")
to = c[c.status == "timeout"].groupby(["algo", "level"]).size()
to_txt = "; ".join(f"{al} {lv}x{lv}: {n}/10" for (al, lv), n in to.items()) or "none"
add("8 failure mode", "classical",
    f"A* timeouts: {int((a.status == 'timeout').sum())}/{len(a)}; timeouts in the study: {to_txt}")

# ---------------- LLM, direct prompt ----------------
m = pd.read_csv(RES / "llm_grid.csv")
add("1 correctness", "LLM", f"{int((m.category == 'correct').sum())}/{len(m)} correct")
add("3 cost", "LLM", f"{med(m.prompt_tokens)} tokens in / {med(m.output_tokens)} tokens out (median)")
add("4 latency", "LLM", f"{med(m.gen_latency_s)} s median / {p95(m.gen_latency_s)} s p95")
rp = pd.read_csv(RES / "repro.csv")
parts = [f"{cond}: {rp[rp.condition == cond].raw_text.nunique()}/5 distinct"
         for cond in rp.condition.unique()]
add("5 reproducibility", "LLM", "; ".join(parts) + " (grid 8x8 #0)")
cats = m.category.value_counts().to_dict()
why = m[m.category == "illegal"].reason.value_counts().to_dict()
add("8 failure mode", "LLM", f"categories {cats}; illegal because {why}; "
    f"cut by token cap: {int((m.done_reason == 'length').sum())}/{len(m)}")

# ---------------- tool-augmented ----------------
tp = RES / "tool_grid.csv"
if tp.exists():
    t = pd.read_csv(tp)
    n = len(t)
    add("1 correctness", "tool", f"{int((t.category == 'correct').sum())}/{n} correct "
        f"(n = {n}, {t['size'].nunique()} sizes)")
    add("3 cost", "tool", f"{med(t.prompt_tokens)} tokens in / {med(t.output_tokens)} tokens out "
        f"(median, all calls) + one A* run")
    add("4 latency", "tool", f"{med(t.gen_latency_s)} s median / {p95(t.gen_latency_s)} s p95")
    add("5 reproducibility", "tool", "not measured")
    add("8 failure mode", "tool",
        f"categories {t.category.value_counts().to_dict()}; "
        f"tool called {int((t.tool_called == True).sum())}/{n}; "
        f"grid copied exactly {int((t.grid_copy_exact == True).sum())}/{n}; "
        f"tool rejected input {int(t.tool_error.notna().sum())}/{n}")
else:
    add("1 correctness", "tool", "(tool_grid.csv not found yet)")

out = pd.DataFrame(rows)
out.to_csv(RES / "scorecard_data.csv", index=False)
for axis in sorted(out.axis.unique()):
    print(f"\n[{axis}]")
    for r in out[out.axis == axis].itertuples():
        print(f"  {r.system:<10} {r.value}")
print("\nsaved results/scorecard_data.csv")
