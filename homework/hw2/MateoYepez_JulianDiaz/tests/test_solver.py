import random
from satlab.solver import solve, verify_assignment
from satlab.validation import solutions


def test_sat_unsat_and_empty():
    assert solve([]).status == 'SAT'
    assert solve([[]]).status == 'UNSAT'
    assert solve([[1],[-1]]).status == 'UNSAT'
    r = solve([[1,2],[-1,3],[-3,-4],[4]])
    assert r.status == 'SAT' and verify_assignment([[1,2],[-1,3],[-3,-4],[4]], r.assignment)


def test_propagation_pure_backtracking():
    assert solve([[1],[-1,2]]).stats['propagations'] >= 2
    assert solve([[1,2]]).stats['pure'] >= 1
    r = solve([[1,2],[-1,2],[1,-2],[-1,-2]])
    assert r.status == 'UNSAT' and r.stats['decisions'] >= 2


def test_timeout_error_missing_assignment():
    assert solve([[1]], timeout=0).status == 'TIMEOUT'
    assert solve([[0]]).status == 'ERROR'
    assert not verify_assignment([[-1]], {})
    assert not verify_assignment([[1]], {1:1})


def test_random_formulas_against_truth_table():
    rng = random.Random(17)
    for _ in range(200):
        clauses = [[rng.choice([-3,-2,-1,1,2,3]) for _ in range(rng.randrange(5))]
                   for _ in range(rng.randrange(10))]
        r = solve(clauses, [1,2,3])
        assert (r.status == 'SAT') == bool(solutions(clauses,[1,2,3]))
        if r.status == 'SAT': assert verify_assignment(clauses,r.assignment)


def test_actual_deadline_interrupts_engine(monkeypatch):
    import time
    import satlab.solver_adapter as adapter
    def slow(*args,**kwargs): time.sleep(.2)
    monkeypatch.setattr(adapter,'dpll',slow)
    started=time.perf_counter()
    assert adapter.solve([[1]],timeout=.01).status=='TIMEOUT'
    assert time.perf_counter()-started<.15
