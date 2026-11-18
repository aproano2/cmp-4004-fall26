"""Pipeline outcome (parser/solver only: this is all the refinement loop may see) and the
post-hoc error taxonomy (uses ground truth: never fed back to the model)."""
from csp import SchemaError, check_schema, normalize_model, solve, validate, norm_color
from llm import extract_json, extract_json_first

CATS = {
    'ok': 'correct',
    'syntax': 'Malformed syntax (won\'t parse)',
    'scope_arity': 'Quantifier scope / arity error',
    'over': 'Valid syntax, over-constrained (UNSAT)',
    'under': 'Valid syntax, under-constrained (premise dropped, wrong solution returned)',
    'wrong': 'Valid model of the wrong problem (hallucinated / altered premises)',
    'timeout': 'Solver timeout',
}
# A-priori detectability from the assignment table + what actually happens for this CSP.
DETECTABLE = {'syntax': 'yes', 'scope_arity': 'yes', 'over': 'yes', 'timeout': 'yes', 'under': 'no', 'wrong': 'no'}


def run_pipeline(raw, timeout_s=5.0):
    """Parse -> schema check -> solve. Returns an outcome whose `feedback` contains ONLY
    parser/solver information (never the ground truth)."""
    out = {'stage': None, 'model': None, 'assignment': None, 'solver_seconds': 0.0, 'feedback': '', 'schema_kind': None}
    try:
        obj = extract_json(raw)
    except ValueError as e:  # includes json.JSONDecodeError
        out.update(stage='parse', feedback=f'Your output could not be parsed as JSON ({e}). Reply with ONLY one valid JSON object with keys "variables", "domains", "constraints".')
        return out
    try:
        check_schema(obj)
    except SchemaError as e:
        out.update(stage='schema', schema_kind=e.kind, feedback=f'The CSP was rejected by the validator: {e}. Fix it and reply with ONLY the corrected JSON object.')
        return out
    model = normalize_model(obj); out['model'] = model
    r = solve(model, timeout_s); out['solver_seconds'] = r['solver_seconds']
    if r['status'] == 'sat':
        out.update(stage='sat', assignment=r['assignment'])
    elif r['status'] == 'unsat':
        out.update(stage='unsat', feedback='The solver reports that this CSP is UNSATISFIABLE: no assignment satisfies all domains and constraints. Re-read the problem statement, correct the model and reply with ONLY the corrected JSON object.')
    else:
        out.update(stage='timeout', feedback=f'The solver timed out after {timeout_s:.0f} s. Reply with ONLY a corrected JSON object.')
    return out


def _edges(m):
    return {frozenset(c) for c in m['constraints']}


def diff_models(model, truth):
    te, me = _edges(truth), _edges(model)
    d = {
        'missing_edges': sorted(tuple(sorted(e)) for e in te - me),
        'extra_edges': sorted(tuple(sorted(e)) for e in me - te),
        'missing_vars': sorted(set(truth['variables']) - set(model['variables'])),
        'extra_vars': sorted(set(model['variables']) - set(truth['variables'])),
        'wider_domains': {}, 'narrower_or_changed_domains': {},
    }
    for v in truth['variables']:
        if v in model['domains']:
            t, m = set(truth['domains'][v]), set(model['domains'][v])
            if m > t: d['wider_domains'][v] = sorted(m)
            elif m != t: d['narrower_or_changed_domains'][v] = sorted(m)
    return d


def label_attempt(outcome, p):
    """Post-hoc label of one pipeline outcome against ground truth."""
    st = outcome['stage']
    if st == 'parse': return 'syntax', 'output is not parseable JSON'
    if st == 'schema':
        return ('scope_arity' if outcome['schema_kind'] in ('scope', 'arity') else 'syntax'), outcome['feedback']
    if st == 'unsat':
        d = diff_models(outcome['model'], p['ground_truth_model']); return 'over', _fmt(d)
    if st == 'timeout': return 'timeout', 'solver exceeded time limit'
    if validate(p['ground_truth_model'], outcome['assignment']): return 'ok', ''
    d = diff_models(outcome['model'], p['ground_truth_model'])
    only_dropped = not d['extra_edges'] and not d['extra_vars'] and not d['missing_vars'] and not d['narrower_or_changed_domains']
    if only_dropped and (d['missing_edges'] or d['wider_domains']): return 'under', _fmt(d)
    return 'wrong', _fmt(d)


def _fmt(d):
    parts = []
    if d['missing_edges']: parts.append('dropped adjacencies: ' + ', '.join('-'.join(e) for e in d['missing_edges']))
    if d['extra_edges']: parts.append('hallucinated adjacencies: ' + ', '.join('-'.join(e) for e in d['extra_edges']))
    if d['wider_domains']: parts.append('dropped colour clue (domain wider than stated): ' + ', '.join(d['wider_domains']))
    if d['narrower_or_changed_domains']: parts.append('domain narrower/changed: ' + ', '.join(f'{v}->{c}' for v, c in d['narrower_or_changed_domains'].items()))
    if d['missing_vars']: parts.append('missing variables: ' + ', '.join(d['missing_vars']))
    if d['extra_vars']: parts.append('extra variables: ' + ', '.join(d['extra_vars']))
    return '; '.join(parts) or 'model differs from ground truth in an unclassified way'


# ---- arm C (direct answer) -------------------------------------------------------------
def classify_direct(raw, p):
    """Returns (assignment_or_None, category, detail, announced). `announced` = the failure is visible
    from the answer + the prompt alone (unparseable / incomplete / colour outside the allowed set),
    i.e. detectable WITHOUT ground truth. Violated adjacency/clue is silent."""
    truth = p['ground_truth_model']
    try:
        obj = extract_json_first(raw)
    except ValueError as e:
        return None, 'unparseable', str(e), True
    ans = obj.get('assignment') if isinstance(obj, dict) else None
    if not isinstance(ans, dict):
        return None, 'unparseable', 'no "assignment" object', True
    # Region names are matched case-insensitively ("r1" == "R1"): a casing slip is not a reasoning error.
    canon = {v.upper(): v for v in truth['variables']}
    ans = {canon.get(str(k).strip().upper(), k): norm_color(v) for k, v in ans.items()}
    if set(ans) != set(truth['variables']):
        return ans, 'incomplete', 'assignment keys differ from the regions in the prompt', True
    if any(c not in ('red', 'green', 'blue') for c in ans.values()):
        return ans, 'invalid_color', 'colour outside {red, green, blue}', True
    if validate(truth, ans): return ans, 'ok', '', False
    viol = [f'{a}-{b}' for a, b in truth['constraints'] if ans[a] == ans[b]]
    clues = [v for v in truth['variables'] if ans[v] not in truth['domains'][v]]
    detail = []
    if viol: detail.append('adjacent regions share a colour: ' + ', '.join(viol))
    if clues: detail.append('colour clue violated: ' + ', '.join(clues))
    return ans, 'silent_wrong', '; '.join(detail), False
