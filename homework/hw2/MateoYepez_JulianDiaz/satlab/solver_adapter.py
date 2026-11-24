"""Unmodified Week 7 engine, with a POSIX main-thread deadline wrapper."""
from collections import Counter
from dataclasses import dataclass, field
import signal
import threading
import time
from .vendor.week07_dpll import dpll
from .validation import validate_cnf, verify_assignment


@dataclass
class SolverResult:
    status: str
    assignment: dict[int, bool] | None = None
    seconds: float = 0.0
    error: str = ''
    stats: dict = field(default_factory=dict)


def solve(clauses: list[list[int]], variables=None, timeout: float = 10) -> SolverResult:
    start = time.perf_counter()
    stats = Counter()
    armed = False
    previous = None
    def expire(signum, frame):
        raise TimeoutError('DPLL deadline exceeded')
    try:
        if timeout <= 0:
            raise TimeoutError('DPLL deadline exceeded')
        ids = set(variables) if variables is not None else {abs(x) for c in clauses for x in c}
        validate_cnf(clauses, ids)
        if threading.current_thread() is not threading.main_thread() or not hasattr(signal, 'setitimer'):
            raise RuntimeError('deadline adapter requires POSIX main thread')
        if signal.getitimer(signal.ITIMER_REAL)[0]:
            raise RuntimeError('another real-time alarm is active')
        previous = signal.signal(signal.SIGALRM, expire)
        signal.setitimer(signal.ITIMER_REAL, timeout)
        armed = True
        assignment = dpll([frozenset(c) for c in clauses], stats=stats)
        if assignment is not None:
            assignment = {v: assignment.get(v, False) for v in sorted(ids)}
            if not verify_assignment(clauses, assignment):
                raise RuntimeError('invalid solver witness')
        result = SolverResult('SAT' if assignment is not None else 'UNSAT', assignment)
    except TimeoutError as exc:
        result = SolverResult('TIMEOUT', error=str(exc))
    except Exception as exc:
        result = SolverResult('ERROR', error=str(exc))
    finally:
        if armed:
            signal.setitimer(signal.ITIMER_REAL, 0)
            signal.signal(signal.SIGALRM, previous)
    result.seconds = time.perf_counter() - start
    result.stats = dict(stats)
    return result
