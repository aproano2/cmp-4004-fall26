"""Uso: python llm_round.py K  -> lee .llm_cache/roundK_response.json (propuesta del LLM), evalúa, guarda y
escribe .llm_cache/round{K+1}_prompt.txt con la retroalimentación (historial de convergencia) que ve el LLM."""
import json, sys, os, time
from tuning import eval_config, feedback_text
C = "../.llm_cache"
k = int(sys.argv[1]); REPLAY = len(sys.argv) > 2 and sys.argv[2] == "--replay"  # re-evalúa propuestas cacheadas sin tocar los prompts originales
prop = json.load(open(f"{C}/round{k}_response.json"))
t0 = time.time()
res = [eval_config(p["n"], p["w"]) for p in prop["configs"]]
json.dump(dict(results=res, eval_seconds=time.time() - t0), open(f"{C}/round{k}_results.json", "w"), indent=1)
hist = []
for j in range(1, k + 1):
    r = json.load(open(f"{C}/round{j}_results.json"))["results"]
    hist.append(feedback_text(r, 4 * (j - 1) + 1))
txt = "HISTORIAL DE CONFIGURACIONES EVALUADAS (PSO, Rastrigin D=10, 25000 evals, 5 seeds de entrenamiento):\n" + "\n".join(hist)
if not REPLAY: open(f"{C}/round{k+1}_prompt.txt", "w").write(txt)
else: open(f"{C}/round{k+1}_feedback_replay_official_budget.txt", "w").write(txt)
print(txt)
