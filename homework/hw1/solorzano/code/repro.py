"""Reproducibilidad: 1 instancia, 5 llamadas idénticas, contar respuestas distintas. Idénticas significa mismo prompt, mismo modelo y misma temperatura, cambia
la semilla. Así cada llamada es un intento independiente con temperatura 0 y la misma semilla, las cinco saldrían de la caché. Por defecto se usa temperatura 0.7.
python repro.py --domain 8puzzle --level 8 --instance-id 1
python repro.py --domain 8puzzle --level 8 --instance-id 1 --temperature 0 --out repro_t0.csv
"""

import argparse
import csv
from collections import Counter
from pathlib import Path

from duel_problems import build_instances, get
from llm import DEFAULT_CACHE, LLM, BackendError, BackendUnavailable
from prompts import llm_messages
from run_duel import RESULTS_DIR
from validator import normalized_path, parse_answer, validate


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--domain", choices=["8puzzle", "grid"], default="8puzzle")
    ap.add_argument("--level", type=int, default=8)
    ap.add_argument("--instance-id", type=int, default=1)
    ap.add_argument("--n-calls", type=int, default=5)
    ap.add_argument("--temperature", type=float, default=0.7)
    ap.add_argument("--backend", default="ollama", choices=["ollama", "manual", ])
    ap.add_argument("--model", default="qwen2.5:3b")
    ap.add_argument("--host", default="http://localhost:11434")
    ap.add_argument("--max-tokens", type=int, default=1024)
    ap.add_argument("--out", default="repro.csv")
    ap.add_argument("--cache-dir", default=str(DEFAULT_CACHE))
    ap.add_argument("--results-dir", default=str(RESULTS_DIR))
    a = ap.parse_args()

    if a.backend == "mock" and (Path(a.results_dir).resolve() == RESULTS_DIR.resolve()
                                or Path(a.cache_dir).resolve() == DEFAULT_CACHE.resolve()):
        raise SystemExit("--backend mock is for testing only: pass --results-dir and --cache-dir "
                         "pointing to a temporary folder")
    inst = get(build_instances(), a.domain, a.level, a.instance_id)
    mock_fn = None
    llm = LLM(a.backend, a.model, a.cache_dir, a.temperature, 0, a.host, a.max_tokens, mock_fn=mock_fn)

    rows = []
    for k in range(1, a.n_calls + 1):
        try:
            text = llm.chat(llm_messages(inst), temperature=a.temperature, seed=k)
        except BackendUnavailable as e:
            raise SystemExit(f"STOPPED: {e}")
        except BackendError as e:
            if "repeat limit" in str(e).lower():          #the model looped; that IS an answer outcome
                rows.append({"instance_id": inst["key"], "call": k, "seed": k, "temperature": a.temperature,
                             "answer": "ABORTED: model stuck repeating tokens", "category": "unparseable",
                             "reported_cost": None, "actual_cost": None, "optimal_cost": inst["optimal_cost"]})
                print(f"call {k}: unparseable          (model stuck repeating tokens, Ollama aborted)")
            else:
                print(f"call {k}: FAILED ({e})")
            continue
        ans = parse_answer(text)
        res = validate(inst, ans)
        rows.append({"instance_id": inst["key"], "call": k, "seed": k, "temperature": a.temperature,
                     "answer": normalized_path(inst["domain"], ans), "category": res["category"],
                     "reported_cost": res["reported_cost"], "actual_cost": res["actual_cost"],
                     "optimal_cost": res["optimal_cost"]})
        print(f"call {k}: {res['category']:20s} {rows[-1]['answer'][:60]}")

    if not rows:
        raise SystemExit("no successful calls; nothing written")
    out = Path(a.results_dir)
    out.mkdir(parents=True, exist_ok=True)
    with open(out / a.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    distinct_answers = len({r["answer"] for r in rows})
    cats = Counter(r["category"] for r in rows)
    print(f"\n{inst['key']}: {len(rows)} calls -> {distinct_answers} distinct answers; outcomes {dict(cats)}")


if __name__ == "__main__":
    main()
