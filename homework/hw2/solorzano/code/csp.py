"""Week 6 studio — the shared CSP engine (GIVEN to you; do not modify).

This is the solver from the Session-6A notebook (`week-06-csp.ipynb`), unchanged:
the binary-constraint `CSP`, `backtrack_search` with four ablation switches
(forward checking, MRV+degree, LCV, AC-3 preprocessing), the `ac3` fixpoint, and
the Sudoku / Australia map-colouring fixtures with their exact instances.

Week 6 is about *inference beats search* — the gain comes from propagation and
ordering, not from a smarter search loop. So the solver is provided. You model a
scheduling problem in ``starter.py`` and build the Logic-LM arm-B pipeline with the
helpers in ``logic_lm.py``.

Interface (identical to the notebook):
    csp.consistent(var, value, assignment)  -> bool  (all-different)
    csp.degree(var)                          -> int
    backtrack_search(csp, use_fc, use_mrv, use_lcv, use_ac3, limit)
        -> (solution_dict | None | "TIMEOUT", counter)   counter["calls"] = backtrack calls
    ac3(csp, domains)                        -> bool (False = proven inconsistent; mutates domains)
    sudoku_csp(grid_string)                  -> CSP
"""
from collections import deque
import time
import itertools
import json
from pathlib import Path


class CSP:
    """Binary-constraint CSP with explicit neighbour lists."""

    def __init__(self, variables, domains, neighbors):
        self.variables = list(variables)
        self.domains = {v: set(domains[v]) for v in variables}
        self.neighbors = neighbors          # var -> set of conflicting vars
        self.pruned = []                    # trail for undo

    def consistent(self, var, value, assignment):
        """All-different: no neighbour already holds this value."""
        return all(assignment.get(n) != value for n in self.neighbors[var])

    def degree(self, var):
        return len(self.neighbors[var])


def sudoku_csp(grid):
    """grid: 81-char string, '.' or '0' for blank."""
    cells = [(r, c) for r in range(9) for c in range(9)]
    neighbors = {}
    for (r, c) in cells:
        peers = set()
        for k in range(9):
            peers.add((r, k))
            peers.add((k, c))
        br, bc = 3 * (r // 3), 3 * (c // 3)
        for dr in range(3):
            for dc in range(3):
                peers.add((br + dr, bc + dc))
        peers.discard((r, c))
        neighbors[(r, c)] = peers

    domains = {}
    for i, (r, c) in enumerate(cells):
        ch = grid[i]
        domains[(r, c)] = {int(ch)} if ch not in ".0" else set(range(1, 10))
    return CSP(cells, domains, neighbors)


def show_sudoku(assignment):
    for r in range(9):
        row = " ".join(str(assignment.get((r, c), ".")) for c in range(9))
        print(row[:5] + "|" + row[6:11] + "|" + row[12:])
        if r in (2, 5):
            print("-" * 5 + "+" + "-" * 5 + "+" + "-" * 5)


# A genuinely hard instance -- "Platinum Blonde"-class, designed to defeat
# naive backtracking.
HARD = ("..............3.85..1.2.......5.7.....4...1...9.......5"
        "......73..2.1........4...9")
EASY = ("53..7....6..195....98....6.8...6...34..8.3..17...2...6"
        ".6....28....419..5....8..79")
MED  = ("4.....8.5.3..........7......2.....6.....8.4......1...."
        "...6.3.7.5..2.....1.4......")


def backtrack_search(csp, use_fc=False, use_mrv=False, use_lcv=False,
                     use_ac3=False, limit=2_000_000):
    counter = {"calls": 0}
    domains = {v: set(csp.domains[v]) for v in csp.variables}

    if any(not domains[v] for v in csp.variables):
        return None, counter

    assignment = {v: next(iter(domains[v])) for v in csp.variables
                  if len(domains[v]) == 1}

    # Los valores iniciales pueden contradecirse antes de empezar la búsqueda.
    for v, value in assignment.items():
        others = {k: x for k, x in assignment.items() if k != v}
        if not csp.consistent(v, value, others):
            return None, counter

    # Propagate the GIVENS before search starts. Without this the domains of
    # blank cells stay full, MRV has nothing to discriminate on, and the whole
    # ablation collapses. (This bug is easy to write and hard to spot -- the
    # solver still returns correct answers, just far too slowly.)
    if use_fc:
        for v, val in assignment.items():
            for n in csp.neighbors[v]:
                if n not in assignment:
                    domains[n].discard(val)

    def select_unassigned():
        unassigned = [v for v in csp.variables if v not in assignment]
        if not use_mrv:
            return unassigned[0]
        return min(unassigned, key=lambda v: (len(domains[v]), -csp.degree(v)))

    def order_values(var):
        vals = list(domains[var])
        if not use_lcv:
            return vals
        # LCV: prefer the value that rules out fewest neighbour options
        def conflicts(val):
            return sum(1 for n in csp.neighbors[var]
                       if n not in assignment and val in domains[n])
        return sorted(vals, key=conflicts)

    def forward_check(var, value):
        """Remove value from unassigned neighbours. Returns trail or None."""
        removed = []
        for n in csp.neighbors[var]:
            if n not in assignment and value in domains[n]:
                domains[n].discard(value)
                removed.append((n, value))
                if not domains[n]:
                    return removed, True      # domain wiped out -> fail
        return removed, False

    def undo(removed):
        for (n, value) in removed:
            domains[n].add(value)

    def recurse():
        counter["calls"] += 1
        if counter["calls"] > limit:
            raise TimeoutError("call limit exceeded")
        if len(assignment) == len(csp.variables):
            return dict(assignment)

        var = select_unassigned()
        for value in order_values(var):
            if csp.consistent(var, value, assignment):
                assignment[var] = value
                removed, wiped = ([], False)
                if use_fc:
                    removed, wiped = forward_check(var, value)
                if not wiped:
                    result = recurse()
                    if result is not None:
                        return result
                if use_fc:
                    undo(removed)
                del assignment[var]
        return None

    try:
        return recurse(), counter
    except TimeoutError:
        return "TIMEOUT", counter


def ac3(csp, domains):
    """Returns False if an inconsistency is found. Mutates `domains`."""
    queue = deque((x, y) for x in csp.variables for y in csp.neighbors[x])

    def revise(x, y):
        removed = False
        for vx in set(domains[x]):
            # all-different: vx survives iff y has some value != vx
            if not any(vy != vx for vy in domains[y]):
                domains[x].discard(vx)
                removed = True
        return removed

    while queue:
        x, y = queue.popleft()
        if revise(x, y):
            if not domains[x]:
                return False
            for z in csp.neighbors[x]:
                if z != y:
                    queue.append((z, x))
    return True


# ---- Australia map colouring (verbatim fixture) -----------------------------

AUS_NEIGHBORS = {
    "WA": {"NT", "SA"}, "NT": {"WA", "SA", "Q"}, "SA": {"WA", "NT", "Q", "NSW", "V"},
    "Q": {"NT", "SA", "NSW"}, "NSW": {"Q", "SA", "V"}, "V": {"SA", "NSW", "T"},
    "T": {"V"},
}
COLORS = {"red", "green", "blue"}


def australia_csp(colors=None):
    """The map-colouring CSP from the notebook. Pass a 2-colour set to make it
    unsatisfiable — the solver then *proves* no colouring exists by exhaustion."""
    colors = colors or COLORS
    return CSP(list(AUS_NEIGHBORS), {v: set(colors) for v in AUS_NEIGHBORS},
               AUS_NEIGHBORS)


def valid_sudoku(sol, csp):
    """Verify a Sudoku solution -- never trust a solver you just wrote."""
    for var, val in sol.items():
        for n in csp.neighbors[var]:
            if sol[n] == val:
                return False
    return len(sol) == 81 and all(1 <= v <= 9 for v in sol.values())


def solution_consistent(sol, csp):
    """Generic check: `sol` is complete and violates no all-different neighbour."""
    if sol in (None, "TIMEOUT"):
        return False
    if len(sol) != len(csp.variables):
        return False
    for var in csp.variables:
        if var not in sol:
            return False
        for n in csp.neighbors[var]:
            if sol.get(n) == sol[var]:
                return False
    return True
