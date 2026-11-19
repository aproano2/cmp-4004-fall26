"""DPLL vs. brute force on random CNFs + edge cases."""
import itertools, random
from sat_solver import solve, validate_cnf, unsat_core


def brute(nv, clauses):
    for bits in itertools.product([False, True], repeat=nv):
        if all(any((bits[abs(l) - 1] if l > 0 else not bits[abs(l) - 1]) for l in c) for c in clauses):
            return True
    return False


def holds(model, clauses):
    return all(any(model[abs(l)] == (l > 0) for l in c) for c in clauses)


random.seed(7)
for _ in range(600):
    nv = random.randint(1, 9)
    clauses = [[random.choice([-1, 1]) * random.randint(1, nv) for _ in range(random.randint(1, 3))]
               for _ in range(random.randint(0, 5 * nv))]
    r = solve(nv, clauses)
    assert (r["status"] == "SAT") == brute(nv, clauses), (nv, clauses)
    if r["status"] == "SAT":
        assert holds(r["model"], clauses) and set(r["model"]) == set(range(1, nv + 1))
assert solve(3, [])["status"] == "SAT"
assert solve(3, [[]])["status"] == "UNSAT"
assert solve(1, [[1], [-1]])["status"] == "UNSAT"
assert solve(2, [[1, -1], [2]])["status"] == "SAT"
core = unsat_core(2, [[1], [-1], [2]])
assert sorted(core) == [0, 1]
for bad in [(0, []), (True, []), (2, [[3]]), (2, [[0]]), (2, [1]), (2, [[1.0]]), (2, [[True]])]:
    try: validate_cnf(*bad); raise SystemExit(f"validate_cnf accepted {bad}")
    except ValueError: pass
print("OK: DPLL agrees with brute force on 600 random CNFs; edge cases and validation pass.")
