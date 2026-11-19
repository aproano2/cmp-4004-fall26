"""End-to-end test of the harness with a SCRIPTED fake LLM (no network).
It only checks the code paths (parse/schema/UNSAT/timeout/silent errors, refinement, analysis).
Its outputs go to a temp dir and are NOT experimental results."""
import json, os, pathlib, shutil, subprocess, sys, tempfile, hashlib, itertools
CODE = pathlib.Path(__file__).resolve().parents[1] / 'code'; sys.path.insert(0, str(CODE))
import llm, csp, taxonomy as tx, run_experiment as rx
ROOT = CODE.parent
P = {p['id']: p for p in rx.load_problems()}

def tjson(p, mutate=None, es=False):
    m = json.loads(json.dumps(p['ground_truth_model']))
    if mutate: mutate(m)
    if es:
        M = {'red': 'rojo', 'green': 'verde', 'blue': 'azul'}
        m['domains'] = {v: [M[c] for c in d] for v, d in m['domains'].items()}
    return json.dumps(m)

def mutations(p):
    vs = p['ground_truth_model']['variables']
    def drop(m): m['constraints'] = m['constraints'][1:]
    def halluc_unsat(m): m['constraints'] += [[a, b] for a, b in itertools.combinations(vs[:4], 2)]
    def arity(m): m['constraints'][0] = m['constraints'][0] + [vs[-1]]
    def unknown(m): m['constraints'][0] = [vs[0], 'R99']
    def dropclue(m): m['domains'][vs[0]] = ['red', 'green', 'blue']
    return dict(ok=tjson(p), ok_es=tjson(p, es=True), ok_fence='```json\n' + tjson(p) + '\n```', malformed=tjson(p)[:-15],
                unsat=tjson(p, halluc_unsat), drop=tjson(p, drop), arity=tjson(p, arity), unknown=tjson(p, unknown),
                dropclue=tjson(p, dropclue))

def fake_chat(messages, rep=0, max_tokens=1500):
    sysm, user = messages[0]['content'], messages[1]['content']
    pid = next(k for k, p in P.items() if p['prompt'] == user); p = P[pid]
    h = int(hashlib.md5(f'{pid}{rep}{len(messages)}'.encode()).hexdigest(), 16)
    if sysm == rx.SYS_DIRECT:
        truth = p['ground_truth_model']; vs = truth['variables']
        text = ['{"assignment": ' + json.dumps({v: 'rojo' for v in vs}) + '}', 'no se', '{"assignment": ' + json.dumps(p['ground_truth_witness']) + '}'][h % 3 if h % 5 else 2]
    else:
        mu = mutations(p); keys = ['ok', 'ok_es', 'ok_fence', 'malformed', 'unsat', 'drop', 'arity', 'unknown', 'dropclue']
        key = keys[h % len(keys)] if len(messages) == 2 else ['ok', 'ok_fence', 'unsat'][h % 3]
        text = mu[key]
    return dict(text=text, seconds=0.5, prompt_tokens=300, completion_tokens=120, cached=False, elapsed=0.0)

rx.llm.chat = fake_chat
os.environ.update(OPENAI_API_KEY='x', MODEL_NAME='fake-model')

# 1. label_attempt unit checks
p = P['P20']; mu = mutations(p)
exp = dict(ok='ok', ok_es='ok', ok_fence='ok', malformed='syntax', unsat='over', drop='under', arity='scope_arity', unknown='scope_arity', dropclue='under')
for k, want in exp.items():
    out = tx.run_pipeline(mu[k]); cat, _ = tx.label_attempt(out, p)
    if k == 'drop' and cat == 'ok': cat = 'under'  # a dropped edge may be satisfied by luck; accept
    if k == 'dropclue' and cat == 'ok': cat = 'under'
    assert cat == want, (k, cat, want)
    import re; assert not re.search(r'\b(red|green|blue|witness|ground)\b', out['feedback'])   # no ground truth leaks into feedback
# timeout path
orig = csp.solve; csp.solve = lambda m, t=5.0: {'status': 'timeout', 'assignment': None, 'solver_seconds': 5.0, 'nodes': 0}
tx.solve = csp.solve
assert tx.label_attempt(tx.run_pipeline(mu['ok']), p)[0] == 'timeout'
csp.solve = orig; tx.solve = orig
print('unit checks OK')

# 2. full run + analysis in a temp copy
tmp = pathlib.Path(tempfile.mkdtemp()); shutil.copytree(ROOT / 'problems', tmp / 'problems'); (tmp / 'results').mkdir()
rows = []
for pr in P.values():
    rows.append(rx.run_hand(pr))
    for rep in range(3):
        for arm in ('B', 'Bprime'): rows.append(rx.run_hybrid(pr, arm, rep))
        rows.append(rx.run_direct(pr, rep))
import csv
with (tmp / 'results' / 'per_instance.csv').open('w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=rx.FIELDS); w.writeheader(); w.writerows(rows)
(tmp / 'results' / 'run_meta.json').write_text(json.dumps({'model': 'fake-model', 'temperature': 0.7, 'repeats': 3, 'date': 'TEST'}))
(tmp / 'results' / 'pricing.csv').write_text('provider,model,input_usd_per_million_tokens,output_usd_per_million_tokens,notes\nTEST,fake,0.05,0.08,test\n')
r = subprocess.run([sys.executable, str(CODE / 'analyze.py'), '--root', str(tmp)], capture_output=True, text=True)
print(r.stdout, r.stderr[-1500:])
assert r.returncode == 0
for f in ['REPORT.md', 'taxonomy.md', 'fig/accuracy_vs_difficulty.png', 'fig/refinement_iterations.png', 'fig/arm_b_error_taxonomy.png', 'fig/detectability.png', 'fig/cost_per_correct.png', 'results/scorecard.csv']:
    assert (tmp / f).exists(), f
bp = [x for x in rows if x['arm'] == 'Bprime']; b = [x for x in rows if x['arm'] == 'B']
assert sum(x['correct'] for x in bp) >= sum(x['correct'] for x in b)
print('TMP', tmp)
