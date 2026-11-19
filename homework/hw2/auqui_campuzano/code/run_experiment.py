"""Runs arms A (hand), B (hybrid), Bprime (hybrid + self-refinement, max 3 iterations), C (direct).

    export OPENAI_API_KEY=... MODEL_NAME=... [OPENAI_BASE_URL=...] [TEMPERATURE=0.7]
    python code/run_experiment.py --repeats 3
    python code/analyze.py            # scorecard, taxonomy.md, figures, REPORT.md

Only the parser/solver message is ever fed back to the model (see taxonomy.run_pipeline).
B and B' share their first attempt (same prompt, same cache entry) so B' >= B by construction
and the B -> B' delta is a clean paired measurement of what solver feedback adds.
"""
from __future__ import annotations
import argparse, csv, json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import csp, llm, taxonomy as tx

ROOT = pathlib.Path(__file__).resolve().parents[1]
SYS_MODEL = ('You translate natural-language graph-coloring problems into a CSP encoded as JSON. '
             'Output ONLY one JSON object with keys: "variables" (array of region names), '
             '"domains" (object mapping EACH region to an array of allowed colours), '
             '"constraints" (array of two-element arrays [regionA, regionB], meaning the two regions must have DIFFERENT colours). '
             'Use the lower-case English colour names "red", "green", "blue". '
             'Do NOT solve the problem. Preserve every stated restriction (including colour clues) and do not add restrictions that are not stated.')
SYS_DIRECT = ('Solve the graph-coloring problem. Return ONLY a JSON object {"assignment": {region: colour, ...}} '
              'assigning every region one allowed colour, using the lower-case English names "red", "green", "blue". '
              'Follow every restriction.')
FIELDS = ['problem_id', 'difficulty', 'arm', 'rep', 'correct', 'status', 'category', 'announced', 'detail',
          'wall_seconds', 'llm_seconds', 'solver_seconds', 'prompt_tokens', 'completion_tokens', 'tokens',
          'iterations', 'cached_calls', 'model_output', 'attempts_json']


def load_problems(d=None):
    return [json.loads(p.read_text()) for p in sorted((d or ROOT / 'problems').glob('*.json'))]


def blank(p, arm, rep):
    return dict(problem_id=p['id'], difficulty=p['difficulty'], arm=arm, rep=rep, correct=0, status='no-answer',
                category='', announced='', detail='', wall_seconds=0.0, llm_seconds=0.0, solver_seconds=0.0,
                prompt_tokens=0, completion_tokens=0, tokens=0, iterations=0, cached_calls=0, model_output='', attempts_json='[]')


def run_hand(p):
    row = blank(p, 'A', 0); t = time.perf_counter()
    out = csp.solve(p['ground_truth_model']); row['solver_seconds'] = out['solver_seconds']
    row['status'] = 'answered' if out['status'] == 'sat' else out['status']
    row['correct'] = int(out['status'] == 'sat' and csp.validate(p['ground_truth_model'], out['assignment']))
    row['category'] = 'ok' if row['correct'] else 'hand_model_error'
    row['wall_seconds'] = time.perf_counter() - t
    return row


def run_direct(p, rep):
    row = blank(p, 'C', rep); t = time.perf_counter(); overhead_llm = 0.0
    r = llm.chat([{'role': 'system', 'content': SYS_DIRECT}, {'role': 'user', 'content': p['prompt']}], rep=rep)
    row.update(llm_seconds=r['seconds'], prompt_tokens=r['prompt_tokens'], completion_tokens=r['completion_tokens'],
               tokens=r['prompt_tokens'] + r['completion_tokens'], iterations=1, model_output=r['text'], cached_calls=int(r['cached']))
    ans, cat, detail, announced = tx.classify_direct(r['text'], p)
    row['category'] = cat; row['detail'] = detail
    row['status'] = 'answered' if cat in ('ok', 'silent_wrong', 'invalid_color') else 'no-answer'
    row['correct'] = int(cat == 'ok')
    row['announced'] = '' if cat == 'ok' else int(announced)
    row['wall_seconds'] = time.perf_counter() - t - r['elapsed'] + r['seconds']
    return row


def run_hybrid(p, arm, rep):
    max_iter = 3 if arm == 'Bprime' else 1
    row = blank(p, arm, rep); t = time.perf_counter(); real_llm = 0.0
    msgs = [{'role': 'system', 'content': SYS_MODEL}, {'role': 'user', 'content': p['prompt']}]
    attempts = []; label = ('', '')
    for i in range(1, max_iter + 1):
        r = llm.chat(msgs, rep=rep); real_llm += r['elapsed']
        out = tx.run_pipeline(r['text'])
        cat, detail = tx.label_attempt(out, p)
        row['llm_seconds'] += r['seconds']; row['solver_seconds'] += out['solver_seconds']
        row['prompt_tokens'] += r['prompt_tokens']; row['completion_tokens'] += r['completion_tokens']
        row['cached_calls'] += int(r['cached']); row['iterations'] = i; row['model_output'] = r['text']
        attempts.append({'iter': i, 'output': r['text'], 'stage': out['stage'], 'category': cat, 'detail': detail,
                         'feedback_sent': out['feedback'] if out['stage'] != 'sat' else ''})
        label = (cat, detail)
        if out['stage'] == 'sat':           # solver is happy: the loop cannot know whether the model is faithful
            row['status'] = 'answered'; row['correct'] = int(cat == 'ok'); break
        msgs = msgs + [{'role': 'assistant', 'content': r['text']}, {'role': 'user', 'content': out['feedback']}]
    row['tokens'] = row['prompt_tokens'] + row['completion_tokens']
    row['category'] = label[0]; row['detail'] = label[1]
    if row['correct']: row['announced'] = ''
    else: row['announced'] = int(row['status'] == 'no-answer')   # solver/parser rejected = announced; answered-but-wrong = silent
    row['attempts_json'] = json.dumps(attempts, ensure_ascii=False)
    row['wall_seconds'] = time.perf_counter() - t - real_llm + row['llm_seconds']
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--arms', default='A,B,Bprime,C'); ap.add_argument('--repeats', type=int, default=3)
    ap.add_argument('--results', default=str(ROOT / 'results')); ap.add_argument('--problems', default=None)
    a = ap.parse_args()
    arms = a.arms.split(','); res = pathlib.Path(a.results); res.mkdir(parents=True, exist_ok=True)
    problems = load_problems(pathlib.Path(a.problems) if a.problems else None)
    needs_llm = any(x in arms for x in ('B', 'Bprime', 'C'))
    cfg = llm.config()
    if needs_llm and (not cfg['api_key'] or not cfg['model']):
        sys.exit('ERROR: set OPENAI_API_KEY and MODEL_NAME (and OPENAI_BASE_URL) before running arms B, Bprime or C.\n'
                 'Nothing was written, so existing results are untouched. Use --arms A to run only the hand arm.')
    rows = []; infra = 0
    for p in problems:
        if 'A' in arms: rows.append(run_hand(p))
        for rep in range(a.repeats if needs_llm else 0):
            for arm in [x for x in arms if x != 'A']:
                try:
                    rows.append(run_direct(p, rep) if arm == 'C' else run_hybrid(p, arm, rep))
                except llm.InfraError as e:
                    infra += 1; r = blank(p, arm, rep); r.update(status='infra-error', category='infrastructure', detail=str(e)[:300]); rows.append(r)
        print(f'{p["id"]} done', flush=True)
    with (res / 'per_instance.csv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows(rows)
    meta = {'model': cfg['model'], 'base_url': cfg['base'], 'temperature': cfg['temperature'], 'repeats': a.repeats,
            'provider': __import__('os').getenv('MODEL_PROVIDER', ''), 'size': __import__('os').getenv('MODEL_SIZE', ''),
            'date': time.strftime('%Y-%m-%d'), 'arms': arms, 'infra_errors': infra}
    if needs_llm: (res / 'run_meta.json').write_text(json.dumps(meta, indent=2))
    print(f'Wrote {len(rows)} rows to {res}/per_instance.csv ({infra} infrastructure errors; re-run to retry them: successful calls are cached).')


if __name__ == '__main__':
    main()
