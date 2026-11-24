"""Strict input checks and independent exhaustive verification."""
from itertools import product


def validate_cnf(clauses: object, variables: set[int]) -> None:
    if not isinstance(clauses, list):
        raise ValueError('clauses must be a list')
    for clause in clauses:
        if not isinstance(clause, list):
            raise ValueError('each clause must be a list')
        for literal in clause:
            if type(literal) is not int or literal == 0 or abs(literal) not in variables:
                raise ValueError(f'invalid variable literal: {literal!r}')


def verify_assignment(clauses: list[list[int]], assignment: dict[int, bool]) -> bool:
    """Missing variables never satisfy a literal; empty clause is false."""
    return all(any(type(assignment.get(abs(lit))) is bool and
                   assignment[abs(lit)] == (lit > 0) for lit in clause)
               for clause in clauses)


def solutions(clauses: list[list[int]], variables: list[int]) -> set[tuple[bool, ...]]:
    """Truth-table oracle, independent of DPLL; bounded to small datasets."""
    if len(variables) > 20:
        raise ValueError('exhaustive verification limited to 20 variables')
    return {bits for bits in product((False, True), repeat=len(variables))
            if verify_assignment(clauses, dict(zip(variables, bits)))}


def cnf_warnings(clauses: list[list[int]]) -> list[str]:
    warnings = []
    if len({tuple(sorted(set(c))) for c in clauses}) != len(clauses):
        warnings.append('duplicate clauses')
    if any(len(set(c)) < len(c) for c in clauses):
        warnings.append('duplicate literals')
    if any(any(-lit in c for lit in c) for c in clauses):
        warnings.append('tautological clause')
    if [] in clauses:
        warnings.append('empty clause: valid UNSAT constraint')
    return warnings
