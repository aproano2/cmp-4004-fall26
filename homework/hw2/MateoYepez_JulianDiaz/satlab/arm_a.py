"""Hand reference CNF, with no LLM dependency."""
from dataclasses import asdict
from .solver import solve


def run(problem: dict, timeout: float) -> dict:
    return asdict(solve(problem['clauses'],problem['variables'].values(),timeout))
