"""CSP spec format + safe evaluator + generic solver for Homework 2 (The Formalizer).

The week-6 engine (``studios/week-06/csp.py``) only understands binary
all-different constraints, and ``logic_lm.build_csp`` only ``alldiff``/``neq``/``eq``.
Industrial problems need capacity, precedence, conditionals and counting, so this
module extends the same JSON idea with *expression* constraints.

Spec format (the same object arm A writes by hand and arm B asks the LLM for)::

    {
      "variables": {"OP1": ["CNC", "Torno"], "T1": [1, 2, 3]},
      "constraints": [
        {"id": "R1", "expr": "alldiff(OP1, OP2, OP3)"},
        {"id": "R2", "expr": "T1 + 2 <= T3"},
        {"id": "R3", "expr": "implies(OP1 == 'CNC', T1 != 3)"}
      ]
    }

Allowed in ``expr``: variable names, int / string literals, ``+ - * // %``,
comparisons (``== != < <= > >= in not in``), ``and or not``, list/tuple literals,
and the functions ``abs, min, max, alldiff(*xs), count(value, *xs),
implies(a, b)``. Anything else (attribute access, imports, unknown names,
lambdas, ...) is rejected *before* evaluation, so LLM-written specs can be run
safely.

Errors raised:
    SpecError  -- malformed spec / disallowed syntax / unknown variable
                  (arm-B taxonomy: "malformed syntax")
"""
from __future__ import annotations

import ast
import time
from typing import Any


class SpecError(Exception):
    """The spec is not a well-formed CSP in this format."""


def _alldiff(*xs):
    return len(set(xs)) == len(xs)


def _count(value, *xs):
    return sum(1 for x in xs if x == value)


def _implies(a, b):
    return (not a) or bool(b)


FUNCS = {"abs": abs, "min": min, "max": max,
         "alldiff": _alldiff, "count": _count, "implies": _implies}

_ALLOWED_NODES = (
    ast.Expression, ast.BoolOp, ast.And, ast.Or, ast.UnaryOp, ast.Not, ast.USub,
    ast.UAdd, ast.BinOp, ast.Add, ast.Sub, ast.Mult, ast.FloorDiv, ast.Mod,
    ast.Compare, ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.In,
    ast.NotIn, ast.Call, ast.Name, ast.Load, ast.Constant, ast.Tuple, ast.List,
)


def compile_expr(expr: str, variables) -> tuple[Any, tuple[str, ...]]:
    """Validate and compile one constraint expression. Returns (code, scope)."""
    if not isinstance(expr, str) or not expr.strip():
        raise SpecError(f"empty or non-string expression: {expr!r}")
    try:
        tree = ast.parse(expr.strip(), mode="eval")
    except SyntaxError as e:
        raise SpecError(f"syntax error in {expr!r}: {e.msg}") from None
    scope = []
    for node in ast.walk(tree):
        if not isinstance(node, _ALLOWED_NODES):
            raise SpecError(f"disallowed syntax {type(node).__name__} in {expr!r}")
        if isinstance(node, ast.Constant) and not isinstance(node.value, (int, str)):
            raise SpecError(f"only int/str literals allowed in {expr!r}")
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name) or node.func.id not in FUNCS:
                raise SpecError(f"unknown function in {expr!r}")
            if node.keywords:
                raise SpecError(f"keyword arguments not allowed in {expr!r}")
        if isinstance(node, ast.Name):
            if node.id in FUNCS:
                continue
            if node.id not in variables:
                raise SpecError(f"unknown variable {node.id!r} in {expr!r}")
            if node.id not in scope:
                scope.append(node.id)
    if not scope:
        raise SpecError(f"constraint mentions no variable: {expr!r}")
    return compile(tree, "<constraint>", "eval"), tuple(scope)


def load_spec(spec: dict):
    """Validate a spec dict. Returns (variables, domains, constraints)."""
    if not isinstance(spec, dict):
        raise SpecError("spec must be a JSON object")
    raw_vars = spec.get("variables")
    if not isinstance(raw_vars, dict) or not raw_vars:
        raise SpecError("'variables' must be a non-empty object")
    variables, domains = [], {}
    for name, dom in raw_vars.items():
        if not isinstance(name, str) or not name.isidentifier() or name in FUNCS:
            raise SpecError(f"bad variable name {name!r}")
        if not isinstance(dom, list) or not dom:
            raise SpecError(f"domain of {name} must be a non-empty list")
        if not all(isinstance(v, (int, str)) and not isinstance(v, bool) for v in dom):
            raise SpecError(f"domain of {name} must contain only ints/strings")
        variables.append(name)
        domains[name] = list(dict.fromkeys(dom))
    raw_cons = spec.get("constraints")
    if not isinstance(raw_cons, list):
        raise SpecError("'constraints' must be a list")
    constraints = []
    for i, c in enumerate(raw_cons):
        expr = c.get("expr") if isinstance(c, dict) else c
        cid = c.get("id", f"C{i+1}") if isinstance(c, dict) else f"C{i+1}"
        code, scope = compile_expr(expr, variables)
        constraints.append((cid, expr, code, scope))
    return variables, domains, constraints


def _holds(code, env):
    try:
        return bool(eval(code, {"__builtins__": {}}, env))  # noqa: S307 (AST-whitelisted)
    except TypeError:
        # e.g. comparing str with int: the model mixed value types -> constraint fails
        return False


def solve(spec: dict, max_solutions: int | None = 2, node_limit: int = 5_000_000):
    """Backtracking + MRV + forward checking over n-ary constraints.

    Returns dict(status, solutions, nodes, seconds) where status is one of
    'unique', 'multiple', 'unsat', 'timeout'. With ``max_solutions=None`` all
    solutions are enumerated (status 'multiple' if more than one).
    """
    variables, domains, constraints = load_spec(spec)
    by_var = {v: [] for v in variables}
    for c in constraints:
        for v in c[3]:
            by_var[v].append(c)

    cur = {v: list(domains[v]) for v in variables}
    assign: dict[str, Any] = {}
    sols: list[dict] = []
    stats = {"nodes": 0}
    env = dict(FUNCS)
    t0 = time.perf_counter()

    # unary constraints: filter domains up front (node consistency)
    for cid, _, code, scope in constraints:
        if len(scope) == 1:
            v = scope[0]
            cur[v] = [x for x in cur[v] if _holds(code, {**env, v: x})]

    class _Stop(Exception):
        pass

    def rec():
        stats["nodes"] += 1
        if stats["nodes"] > node_limit:
            raise TimeoutError
        if len(assign) == len(variables):
            sols.append(dict(assign))
            if max_solutions is not None and len(sols) >= max_solutions:
                raise _Stop
            return
        var = min((v for v in variables if v not in assign),
                  key=lambda v: (len(cur[v]), -len(by_var[v])))
        for val in list(cur[var]):
            assign[var] = val
            env[var] = val
            ok = True
            for _, _, code, scope in by_var[var]:
                if all(s in assign for s in scope) and not _holds(code, env):
                    ok = False
                    break
            pruned = []
            if ok:  # forward checking on constraints with one free variable
                for _, _, code, scope in by_var[var]:
                    free = [s for s in scope if s not in assign]
                    if len(free) != 1:
                        continue
                    u = free[0]
                    keep = []
                    for x in cur[u]:
                        env[u] = x
                        if _holds(code, env):
                            keep.append(x)
                        else:
                            pruned.append((u, x))
                    env.pop(u, None)
                    cur[u] = keep
                    if not keep:
                        ok = False
                        break
            if ok:
                rec()
            for u, x in reversed(pruned):
                cur[u].append(x)
            del assign[var]
            env.pop(var, None)

    status = None
    try:
        rec()
    except _Stop:
        pass
    except TimeoutError:
        status = "timeout"
    secs = time.perf_counter() - t0
    if status is None:
        status = {0: "unsat", 1: "unique"}.get(len(sols), "multiple")
    return {"status": status, "solutions": sols, "nodes": stats["nodes"], "seconds": secs}


def check_assignment(spec: dict, assignment: dict):
    """Evaluate every constraint on a full assignment. Returns list of (id, expr, ok)."""
    variables, domains, constraints = load_spec(spec)
    missing = [v for v in variables if v not in assignment]
    if missing:
        raise SpecError(f"assignment misses variables {missing}")
    bad_dom = [v for v in variables if assignment[v] not in domains[v]]
    env = {**FUNCS, **{v: assignment[v] for v in variables}}
    out = [("domain", "valores dentro de sus dominios", not bad_dom)]
    out += [(cid, expr, _holds(code, env)) for cid, expr, code, _ in constraints]
    return out
