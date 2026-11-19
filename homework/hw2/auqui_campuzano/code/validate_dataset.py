"""Independent check of the hand-written ground truth.
It re-derives the CSP from the *text of each prompt* (regexes, no shared code with the generator)
and compares it with `ground_truth_model`, then solves it and validates the stored witness."""
import json, pathlib, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from csp import solve, validate
ROOT = pathlib.Path(__file__).resolve().parents[1]
ES = {'rojo': 'red', 'verde': 'green', 'azul': 'blue'}
files = sorted((ROOT / 'problems').glob('*.json'))
assert len(files) >= 20, f'Expected >= 20 problems, found {len(files)}'
counts = {'easy': 0, 'medium': 0, 'hard': 0}; lines = []
for f in files:
    p = json.loads(f.read_text()); counts[p['difficulty']] += 1; m = p['ground_truth_model']; txt = p['prompt']
    regions = re.findall(r'R\d+', txt.split('Los colores')[0])
    edges = {frozenset(e) for e in re.findall(r'(R\d+) no puede tener el mismo color que (R\d+)', txt)}
    clues = dict(re.findall(r'(R\d+) debe ser (rojo|verde|azul)', txt))
    assert set(m['variables']) == set(regions), (p['id'], 'variables differ from prompt')
    assert {frozenset(c) for c in m['constraints']} == edges, (p['id'], 'constraints differ from prompt')
    for v in regions:
        want = [ES[clues[v]]] if v in clues else ['red', 'green', 'blue']
        assert m['domains'][v] == want, (p['id'], v, 'domain differs from prompt')
    dm = p['difficulty_metric']
    assert (dm['variables'], dm['binary_constraints'], dm['fixed_color_clues']) == (len(regions), len(edges), len(clues)), (p['id'], 'difficulty metric mismatch')
    r = solve(m); assert r['status'] == 'sat', (p['id'], r['status']); assert validate(m, r['assignment'])
    assert validate(m, p['ground_truth_witness']), (p['id'], 'stored witness invalid')
    lines.append(f"{p['id']} {p['difficulty']:6} vars={len(regions)} edges={len(edges)} clues={len(clues)}  prompt<->model OK")
print('\n'.join(lines)); print(f'DATASET VALID. {len(files)} instances, difficulty {counts}; ground truth matches prompt text, is satisfiable, witness valid.')
