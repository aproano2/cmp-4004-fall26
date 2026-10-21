"""repro_llm.py -- reproducibility: ONE instance, FIVE identical calls, count the
distinct answers (scorecard axis 5). Two decoding conditions on the same instance:
  temperature 0, seed 0   (the setting used for the whole duel)
  temperature 0.8, no seed (ordinary sampling; the server picks a random seed)
Replicates 1..5 are used so none of these calls collides with the main-run cache entry.
Writes ../results/repro.csv.   Run: python3 repro_llm.py
"""
import csv
import time
from pathlib import Path

import duel_lib as D
import gridworld as GW
import llm_client as L

HERE = Path(__file__).parent
SIZE, IDX = 8, 0
CONDITIONS = [("temp0_seed0", 0.0, 0), ("temp0.8_noseed", 0.8, None)]

grid = GW.load_instances(HERE / "instances_grid.json")[SIZE][IDX]
msgs = [{"role": "user", "content": D.prompt_for(grid, "direct")}]
rows = []
t0 = time.perf_counter()
for name, temp, seed in CONDITIONS:
    for rep in range(1, 6):
        rec = L.chat(msgs, temperature=temp, seed=seed, num_predict=200,
                     replicate=rep, tag=f"repro_{name}_r{rep}")
        v = D.validate(grid, rec["text"])
        rows.append({"condition": name, "replicate": rep, "path": v["path"],
                     "reported_cost": v["reported_cost"], "category": v["category"],
                     "output_tokens": rec["output_tokens"], "key": rec["key"],
                     "raw_text": rec["text"]})
        print(f"[{name} #{rep}] {v['category']:<10} path={str(v['path'])[:40]!r} "
              f"cost={v['reported_cost']} cached={rec['cached']}", flush=True)

with open(HERE.parent / "results" / "repro.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)

print(f"\ninstance: {SIZE}x{SIZE} #{IDX}  ({time.perf_counter() - t0:.0f}s)")
for name, _, _ in CONDITIONS:
    r = [x for x in rows if x["condition"] == name]
    print(f"  {name:<16} distinct raw replies: {len({x['raw_text'] for x in r})}/5   "
          f"distinct (path, cost): {len({(x['path'], x['reported_cost']) for x in r})}/5")
