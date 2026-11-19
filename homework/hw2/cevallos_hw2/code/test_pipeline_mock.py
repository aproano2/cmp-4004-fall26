"""End-to-end test with a FAKE LLM that injects known faults. It validates the harness (parsing, refinement loop,
taxonomy classifier, analysis) — it produces NO real results and writes only to a temp dir."""
import itertools, json, tempfile
from pathlib import Path

import llm, run_experiment, analyze
from encoding import encode_graph

ROOT = Path(__file__).resolve().parents[1]
PROBLEMS = json.loads((ROOT / "problems" / "dataset.json").read_text(encoding="utf-8"))[:12]
SEEN_PROMPTS = []


def cnf_json(nv, clauses): return json.dumps({"num_vars": nv, "clauses": clauses})


def mock_backend(prompt, temperature, seed):
    SEEN_PROMPTS.append(prompt)
    p = next(q for q in PROBLEMS if q["prompt_es"] in prompt)
    i = PROBLEMS.index(p) % 7
    nv, ref = encode_graph(p)
    n = len(p["vertices"]); k = 3
    feedback = "El solver reportó" in prompt
    resp = ""
    if "Resuelve el siguiente" in prompt:                        # arm C
        gt = dict(p["ground_truth"])
        if i == 1: a, b = p["edges"][0]; gt[b] = gt[a]           # silent edge violation
        if i == 2: resp = "no sé"; gt = None                     # unparsable
        if i == 3: gt["A"] = "morado"                            # schema error
        resp = resp or json.dumps({"colors": gt})
    elif i == 0:                                                  # perfect translation
        resp = cnf_json(nv, ref)
    elif i == 1:                                                  # malformed; repaired only on 2nd feedback round
        resp = cnf_json(nv, ref) if "ATTEMPT2" in prompt else ("{'num_vars': ..., ATTEMPT2" if feedback else "{'num_vars': ...")
    elif i == 2:                                                  # drops one edge entirely -> silent (never fixable)
        a, b = p["edges"][0]
        from encoding import var_id
        idx = {v: j for j, v in enumerate(p["vertices"])}
        drop = {frozenset([-var_id(idx[a], c), -var_id(idx[b], c)]) for c in range(k)}
        resp = cnf_json(nv, [c for c in ref if frozenset(c) not in drop])
    elif i == 3:                                                  # hallucinated K4 among first 4 vertices -> UNSAT; fixed by feedback
        if feedback: resp = cnf_json(nv, ref)
        else:
            extra = [[-(a * k + c + 1), -(b * k + c + 1)] for a, b in itertools.combinations(range(4), 2) for c in range(k)]
            resp = cnf_json(nv, ref + extra)
    elif i == 4:                                                  # nearly empty CNF -> decode error; fixed by feedback
        resp = cnf_json(nv, ref if feedback else [[nv]])   # nearly empty model -> most vertices get no colour
    elif i == 5:                                                  # wrong num_vars -> schema error; fixed by feedback
        resp = cnf_json(nv if feedback else nv + 1, ref)
    else:                                                         # literal out of range -> schema; never fixed
        resp = cnf_json(nv, ref + [[nv + 5]])
    return {"response": resp, "prompt_tokens": len(prompt) // 4, "completion_tokens": len(resp) // 4,
            "done_reason": "stop", "llm_time_s": 0.01}


tmp = Path(tempfile.mkdtemp())
llm.CACHE = tmp / "cache"; llm.BACKEND = mock_backend; llm.MODEL = "MOCK"
run_experiment.main(["--runs", "1", "--temperature", "0", "--limit", "12", "--problems", str(ROOT / "problems" / "dataset.json"),
                     "--outdir", str(tmp / "results")])
analyze.main(["--resdir", str(tmp / "results"), "--figdir", str(tmp / "fig"), "--taxonomy-md", str(tmp / "taxonomy.md"),
              "--price-in", "0.1", "--price-out", "0.2"])

import csv
rows = list(csv.DictReader((tmp / "results" / "metrics.csv").open(encoding="utf-8")))
get = lambda pid, arm: next(r for r in rows if r["problem_id"] == pid and r["arm"] == arm)
ids = [p["id"] for p in PROBLEMS]
assert all(get(pid, "A")["correct"] == "True" for pid in ids)                              # hand arm = ceiling
assert get(ids[0], "B")["correct"] == "True" and get(ids[0], "B_prime")["attempts"] == "1"
assert get(ids[1], "B")["status"] == "PARSE_ERROR" and get(ids[1], "B_prime")["correct"] == "True" and get(ids[1], "B_prime")["attempts"] == "3"   # fixed only in the 2nd feedback round
assert get(ids[2], "B")["outcome"] in ("incorrect", "correct")                             # silent: may or may not hit a wrong colouring
assert get(ids[3], "B")["status"] == "UNSAT" and get(ids[3], "B_prime")["correct"] == "True"
assert get(ids[4], "B")["status"] == "DECODE_ERROR" and get(ids[4], "B_prime")["correct"] == "True"
assert get(ids[5], "B")["status"] == "SCHEMA_ERROR" and get(ids[5], "B_prime")["correct"] == "True"
assert get(ids[6], "B")["status"] == "SCHEMA_ERROR" and get(ids[6], "B_prime")["correct"] == "False" and get(ids[6], "B_prime")["attempts"] == "3"
assert get(ids[1], "C")["outcome"] == "incorrect" and get(ids[1], "C")["announced_failure"] == "False"   # silent C failure
assert get(ids[2], "C")["status"] == "PARSE_ERROR" and get(ids[2], "C")["announced_failure"] == "True"
assert get(ids[3], "C")["status"] == "SCHEMA_ERROR"
# cache replay must keep original latency (regression for the llm_time_s = 0 bug)
assert float(get(ids[0], "B_prime")["llm_time_s"]) > 0
# the refinement prompt never contains the ground truth
gts = [json.dumps(p["ground_truth"]) for p in PROBLEMS]
assert not any(gt in pr for gt in gts for pr in SEEN_PROMPTS if "Resuelve" not in pr)
assert not any("ground_truth" in pr or "ground truth" in pr.lower() for pr in SEEN_PROMPTS)
tax = json.loads((tmp / "results" / "taxonomy.json").read_text(encoding="utf-8"))
cats = {t["category"] for t in tax}
assert any(c.startswith("Malformed") for c in cats) and any("UNSAT" in c for c in cats) and any("decoder" in c for c in cats)
assert not any("HARNESS BUG" in c or "Classifier error" in c for c in cats), cats
t3 = next(t for t in tax if t["problem_id"] == ids[3]); assert "alucinadas" in t3["subcause"], t3["subcause"]
t4 = next(t for t in tax if t["problem_id"] == ids[4]); assert "falta 'al menos un color'" in t4["subcause"], t4["subcause"]
for fn in ["scorecard.csv", "scorecard.md", "by_difficulty.csv", "detectability.csv", "cost.csv", "refinement.csv", "taxonomy_counts.csv"]:
    assert (tmp / "results" / fn).exists(), fn
assert len(list((tmp / "fig").glob("*.png"))) >= 5 and (tmp / "taxonomy.md").exists()
print("OK: fault-injection pipeline test passed.\n---- scorecard (MOCK, not real data) ----")
print((tmp / "results" / "scorecard.md").read_text(encoding="utf-8"))
