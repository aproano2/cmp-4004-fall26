"""Small, dependency-free DPLL SAT solver. Literals are signed 1-based integers.

Changes vs. the first version
- unit propagation recomputes the unit clause each pass (no stale unit list);
- clauses are de-duplicated / tautologies dropped up-front;
- returned models are *complete* (variables the search never needed are False);
- `unsat_core` (deletion based) is provided for the optional "rich" feedback ablation.
"""
from time import perf_counter


class SATTimeout(Exception):
    pass


def simplify(clauses, lit):
    """Assign `lit` true. Returns None if an empty clause appears (conflict)."""
    out, neg = [], -lit
    for clause in clauses:
        if lit in clause:
            continue
        new_clause = [x for x in clause if x != neg]
        if not new_clause:
            return None
        out.append(new_clause)
    return out


def unit_propagate(clauses, assignment):
    while True:
        unit = next((c[0] for c in clauses if len(c) == 1), None)
        if unit is None:
            return clauses, assignment
        var, val = abs(unit), unit > 0
        if var in assignment and assignment[var] != val:
            return None, assignment
        assignment[var] = val
        clauses = simplify(clauses, unit)
        if clauses is None:
            return None, assignment


def dpll(clauses, assignment, deadline):
    if perf_counter() > deadline:
        raise SATTimeout("solver timeout")
    clauses, assignment = unit_propagate(clauses, assignment)
    if clauses is None:
        return None
    if not clauses:
        return assignment
    clause = min(clauses, key=len)          # branch on a var of the shortest clause
    var = abs(clause[0])
    for val in (True, False):
        lit = var if val else -var
        nxt = simplify(clauses, lit)
        if nxt is None:
            continue
        nxt_assignment = dict(assignment)
        nxt_assignment[var] = val
        result = dpll(nxt, nxt_assignment, deadline)
        if result is not None:
            return result
    return None


def _normalise(clauses):
    out = []
    for c in clauses:
        c = list(dict.fromkeys(c))                      # drop duplicate literals
        if any(-l in c for l in c):                     # tautology
            continue
        out.append(c)
    return out


def solve(num_vars, clauses, timeout_s=5.0):
    start = perf_counter()
    deadline = start + timeout_s
    try:
        if any(len(c) == 0 for c in clauses):
            model = None
        else:
            model = dpll(_normalise(clauses), {}, deadline)
        if model is None:
            return {"status": "UNSAT", "model": {}, "time_s": perf_counter() - start}
        full = {v: model.get(v, False) for v in range(1, num_vars + 1)}
        return {"status": "SAT", "model": full, "time_s": perf_counter() - start}
    except SATTimeout:
        return {"status": "TIMEOUT", "model": {}, "time_s": perf_counter() - start}


def validate_cnf(num_vars, clauses):
    """Structural validation. Raises ValueError with a message that is safe to show the LLM."""
    if isinstance(num_vars, bool) or not isinstance(num_vars, int) or num_vars < 1:
        raise ValueError("num_vars debe ser un entero positivo")
    if not isinstance(clauses, list):
        raise ValueError("clauses debe ser una lista")
    for i, clause in enumerate(clauses):
        if not isinstance(clause, list):
            raise ValueError(f"la cláusula {i} no es una lista")
        for lit in clause:
            if isinstance(lit, bool) or not isinstance(lit, int) or lit == 0 or abs(lit) > num_vars:
                raise ValueError(f"literal inválido en la cláusula {i}: {lit!r} (debe ser entero no nulo con |lit| <= {num_vars})")
    return True


def unsat_core(num_vars, clauses, budget_s=3.0, per_call_s=1.0):
    """Deletion-based UNSAT core (indices into `clauses`). May be non-minimal if the budget runs out."""
    deadline = perf_counter() + budget_s
    core = list(range(len(clauses)))
    i = 0
    while i < len(core) and perf_counter() < deadline:
        trial = [clauses[j] for k, j in enumerate(core) if k != i]
        if solve(num_vars, trial, timeout_s=per_call_s)["status"] == "UNSAT":
            core.pop(i)
        else:
            i += 1
    return core
