"""Small, auditable finite-domain CSP solver (backtracking, MRV + degree tie-break)
plus schema checking and colour normalisation for LLM-produced models."""
from __future__ import annotations
import time

# The prompts are in Spanish; models may answer with Spanish colour names.
COLOR_ALIASES = {'rojo': 'red', 'verde': 'green', 'azul': 'blue'}


class SchemaError(ValueError):
    """kind: 'syntax' (wrong shape/types), 'arity' (constraint is not a pair / self-loop),
    'scope' (variable used but not declared, or declared without domain)."""
    def __init__(self, msg, kind='syntax'):
        super().__init__(msg)
        self.kind = kind


def norm_color(c):
    if isinstance(c, str):
        c = c.strip().lower()
        return COLOR_ALIASES.get(c, c)
    return c


def normalize_model(m):
    """Return a copy with colour names normalised (only touches domain values)."""
    out = dict(m)
    out['domains'] = {v: [norm_color(c) for c in d] for v, d in m['domains'].items()}
    return out


def check_schema(m):
    if not isinstance(m, dict):
        raise SchemaError('top-level JSON value must be an object', 'syntax')
    for k in ('variables', 'domains', 'constraints'):
        if k not in m:
            raise SchemaError(f'missing key "{k}"', 'syntax')
    vs, ds, cs = m['variables'], m['domains'], m['constraints']
    if not isinstance(vs, list) or not vs or not all(isinstance(v, str) for v in vs):
        raise SchemaError('"variables" must be a non-empty array of strings', 'syntax')
    if len(set(vs)) != len(vs):
        raise SchemaError('"variables" contains duplicates', 'syntax')
    if not isinstance(ds, dict):
        raise SchemaError('"domains" must be an object mapping variable -> array of colours', 'syntax')
    for v in vs:
        if v not in ds:
            raise SchemaError(f'variable "{v}" has no domain', 'scope')
    for v, d in ds.items():
        if v not in vs:
            raise SchemaError(f'domain given for undeclared variable "{v}"', 'scope')
        if not isinstance(d, list) or not d or not all(isinstance(c, str) for c in d):
            raise SchemaError(f'domain of "{v}" must be a non-empty array of strings', 'syntax')
    if not isinstance(cs, list):
        raise SchemaError('"constraints" must be an array of [a, b] pairs', 'syntax')
    for c in cs:
        if not isinstance(c, (list, tuple)):
            raise SchemaError(f'constraint {c!r} is not an array', 'syntax')
        if len(c) != 2:
            raise SchemaError(f'constraint {list(c)!r} has arity {len(c)}; expected exactly 2 variables', 'arity')
        a, b = c
        if not (isinstance(a, str) and isinstance(b, str)):
            raise SchemaError(f'constraint {list(c)!r} must contain variable names (strings)', 'syntax')
        if a not in vs or b not in vs:
            bad = a if a not in vs else b
            raise SchemaError(f'constraint {list(c)!r} uses undeclared variable "{bad}"', 'scope')
        if a == b:
            raise SchemaError(f'constraint {list(c)!r} relates a variable to itself', 'arity')


def solve(model, timeout_s=5.0):
    start = time.perf_counter()
    variables = model['variables']
    domains = {v: list(model['domains'][v]) for v in variables}
    constraints = [tuple(c) for c in model['constraints']]
    neighbors = {v: set() for v in variables}
    for a, b in constraints:
        neighbors[a].add(b); neighbors[b].add(a)
    assignment = {}; nodes = 0

    def consistent(v, val):
        return all(not (n in assignment and assignment[n] == val) for n in neighbors[v])

    def backtrack():
        nonlocal nodes
        if time.perf_counter() - start > timeout_s:
            raise TimeoutError('solver timeout')
        if len(assignment) == len(variables):
            return dict(assignment)
        un = [v for v in variables if v not in assignment]
        v = min(un, key=lambda x: (sum(1 for z in domains[x] if consistent(x, z)), -len(neighbors[x]), x))
        for val in domains[v]:
            nodes += 1
            if consistent(v, val):
                assignment[v] = val
                result = backtrack()
                if result is not None:
                    return result
                del assignment[v]
        return None

    try:
        answer = backtrack(); status = 'sat' if answer is not None else 'unsat'
    except TimeoutError:
        answer = None; status = 'timeout'
    return {'status': status, 'assignment': answer, 'solver_seconds': time.perf_counter() - start, 'nodes': nodes}


def validate(model, assignment):
    """True iff assignment gives every variable a value from its domain and violates no constraint."""
    if not isinstance(assignment, dict):
        return False
    try:
        if set(assignment) != set(model['variables']):
            return False
        if any(assignment[v] not in model['domains'][v] for v in model['variables']):
            return False
        return all(assignment[a] != assignment[b] for a, b in model['constraints'])
    except TypeError:
        return False
