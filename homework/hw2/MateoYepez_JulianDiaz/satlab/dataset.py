"""Dataset provenance, structural metrics and independent validation."""
import hashlib
import json
from pathlib import Path
from .validation import validate_cnf, verify_assignment, solutions
from .solver import solve

ROOT = Path(__file__).resolve().parents[1]


def load_dataset(path: Path = ROOT / 'problems') -> list[dict]:
    return [json.loads(p.read_text()) for p in sorted(path.glob('sat_*.json'))]


def hashes(path: Path = ROOT / 'problems') -> dict:
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(path.glob('*.json'))}


def public_problem(problem: dict) -> dict:
    """Whitelist boundary: private reference data never enters arm code."""
    return {k: problem[k] for k in ('id', 'difficulty', 'prompt', 'variables')}


def structural(problem: dict) -> dict:
    clauses = problem['clauses']
    n = len(clauses)
    literals = sum(map(len, clauses))
    return {'problem_id': problem['id'], 'difficulty': problem['difficulty'],
            'variables': len(problem['variables']), 'clauses': n, 'literals': literals,
            'mean_clause_length': literals / n if n else 0,
            'unit_clause_ratio': sum(len(c) == 1 for c in clauses) / n if n else 0}


def validate_dataset(problems: list[dict]) -> list[dict]:
    records = []
    if len(problems) != 20 or len({p['id'] for p in problems}) != 20:
        raise ValueError('expected exactly 20 distinct original problems')
    if {d: sum(p['difficulty'] == d for p in problems) for d in ('easy','medium','hard')} != {'easy':6,'medium':8,'hard':6}:
        raise ValueError('unexpected difficulty distribution')
    for p in problems:
        issues = []
        ids = sorted(p['variables'].values())
        if any(type(v) is not int or v <= 0 for v in ids) or len(set(ids)) != len(ids):
            raise ValueError('invalid variable map')
        validate_cnf(p['clauses'], set(ids))
        oracle = solutions(p['clauses'], ids)
        status = 'SAT' if oracle else 'UNSAT'
        gt = p['ground_truth']
        if status != gt['status']:
            issues.append('documented status disagrees with exhaustive oracle')
        if gt['status'] == 'SAT':
            witness = gt.get('witness', {})
            if set(witness) != set(p['variables']) or not verify_assignment(p['clauses'], {p['variables'][k]:v for k,v in witness.items() if k in p['variables']}):
                issues.append('documented SAT witness invalid or incomplete')
        elif gt.get('witness'):
            issues.append('UNSAT has a witness')
        result = solve(p['clauses'], ids)
        if result.status != status:
            issues.append('DPLL disagrees with exhaustive oracle')
        records.append({**structural(p), 'expected_status':gt['status'], 'oracle_status':status,
                        'solution_count':len(oracle), 'solver_status':result.status,
                        'valid':not issues, 'issues':issues})
    return records
