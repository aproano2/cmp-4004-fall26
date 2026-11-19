"""Public solver interface; algorithm is vendored unchanged from Week 7."""
from .solver_adapter import SolverResult, solve
from .validation import verify_assignment
__all__ = ['SolverResult', 'solve', 'verify_assignment']
