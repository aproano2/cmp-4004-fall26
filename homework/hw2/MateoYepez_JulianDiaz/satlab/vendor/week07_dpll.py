"""Week 7 studio — the shared reasoning engine (GIVEN to you; do not modify).

This is the DPLL solver, the entailment check, and the Wumpus-World encoding
from the Session-A notebook (``week-07-dpll-sat.ipynb``), unchanged. Week 7 is
about building a *sound agent* on top of a solver and comparing it against an
LLM — not about re-implementing DPLL. So the solver is provided. You write the
agent in ``starter.py``.

Representation (DIMACS convention): a CNF formula is a list of ``frozenset``s of
ints. Positive ``n`` means variable *n*; negative means its negation.

The central identity of the unit — and the reason a SAT solver is a
general-purpose reasoning engine — is one line:

    KB ⊨ α   iff   KB ∧ ¬α  is unsatisfiable            (see ``entails``)

Interface:
    dpll(clauses[, assignment][, stats])  -> satisfying assignment dict | None
    negate_cnf(clauses)                   -> CNF of the negation (unit clauses)
    entails(kb_clauses, alpha_clauses)    -> bool
    wumpus_physics()                      -> CNF list for the 4×4 breeze/pit law
    kb_from_percepts(percepts)            -> physics + percept unit clauses
    classify(kb, x, y)                    -> "SAFE (proved)" | "PIT (proved)" | "UNKNOWN"
"""
import json
from collections import Counter
from pathlib import Path


# ---- 1. representation ------------------------------------------------------

class Vars:
    """Name↔int symbol table. Variables are ints; we keep names for printing."""

    def __init__(self):
        self.by_name, self.by_id = {}, {}

    def __call__(self, name):
        if name not in self.by_name:
            i = len(self.by_name) + 1
            self.by_name[name] = i
            self.by_id[i] = name
        return self.by_name[name]

    def name(self, lit):
        return ("¬" if lit < 0 else "") + self.by_id[abs(lit)]


def clause_str(c, V):
    return "(" + " ∨ ".join(V.name(l) for l in sorted(c, key=abs)) + ")"


# ---- 2. DPLL ----------------------------------------------------------------

def dpll(clauses, assignment=None, stats=None):
    """Returns a satisfying assignment dict, or None if unsatisfiable."""
    assignment = dict(assignment or {})
    if stats is None:
        stats = Counter()
    stats["calls"] += 1

    # ---- 1. unit propagation, to fixpoint -------------------------------
    changed = True
    while changed:
        changed = False
        for clause in clauses:
            unassigned, satisfied = [], False
            for l in clause:
                v = assignment.get(abs(l))
                if v is None:
                    unassigned.append(l)
                elif v == (l > 0):
                    satisfied = True
                    break
            if satisfied:
                continue
            if not unassigned:
                stats["conflicts"] += 1
                return None                       # clause falsified
            if len(unassigned) == 1:              # forced
                lit = unassigned[0]
                assignment[abs(lit)] = (lit > 0)
                stats["propagations"] += 1
                changed = True

    # ---- 2. pure literal elimination ------------------------------------
    remaining = [c for c in clauses
                 if not any(assignment.get(abs(l)) == (l > 0) for l in c)]
    all_lits = {l for c in remaining for l in c if abs(l) not in assignment}
    for lit in all_lits:
        if -lit not in all_lits and abs(lit) not in assignment:
            assignment[abs(lit)] = (lit > 0)
            stats["pure"] += 1

    # ---- 3. base case ----------------------------------------------------
    if all(any(assignment.get(abs(l)) == (l > 0) for l in c) for c in clauses):
        return assignment

    # ---- 4. branch -------------------------------------------------------
    unassigned = [abs(l) for c in clauses for l in c if abs(l) not in assignment]
    if not unassigned:
        return None
    var = unassigned[0]
    for value in (True, False):
        stats["decisions"] += 1
        result = dpll(clauses, {**assignment, var: value}, stats)
        if result is not None:
            return result
    return None


# ---- 3. the central identity, in code ---------------------------------------

def negate_cnf(clauses):
    """Negate a CNF formula. Only correct for a CONJUNCTION OF UNIT clauses,
    which is all we need for entailment queries about single literals."""
    lits = [next(iter(c)) for c in clauses if len(c) == 1]
    assert len(lits) == len(clauses), "negate_cnf: need unit clauses only"
    # ¬(a ∧ b) = (¬a ∨ ¬b)  -- one clause
    return [frozenset(-l for l in lits)]


def entails(kb_clauses, alpha_clauses):
    """KB ⊨ α  iff  KB ∧ ¬α is unsatisfiable."""
    return dpll(kb_clauses + negate_cnf(alpha_clauses)) is None


# ---- 4. the Wumpus World ----------------------------------------------------
# A 4×4 grid. Pits cause a breeze in adjacent squares. The agent must move only
# to squares it can PROVE are safe. P(x,y) = "pit at (x,y)"; B(x,y) = "breeze
# at (x,y)". Physics: a square is breezy IFF some neighbour has a pit.

N = 4
W = Vars()


def Pv(x, y):
    return W(f"P{x}{y}")


def Bv(x, y):
    return W(f"B{x}{y}")


def neighbours(x, y):
    return [(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
            if 1 <= x + dx <= N and 1 <= y + dy <= N]


def wumpus_physics():
    """B(x,y) <-> (P(n1) v P(n2) v ...) for every square, in CNF."""
    clauses = []
    for x in range(1, N + 1):
        for y in range(1, N + 1):
            b = Bv(x, y)
            ns = [Pv(a, c) for a, c in neighbours(x, y)]
            # B -> (P1 v P2 v ...)   ==>  (-B v P1 v P2 v ...)
            clauses.append(frozenset([-b] + ns))
            # (P1 v P2 v ...) -> B   ==>  (-Pi v B) for each i
            for p in ns:
                clauses.append(frozenset({-p, b}))
    return clauses


def kb_from_percepts(percepts):
    """Assemble a KB: the breeze/pit physics plus one unit clause per percept.

    ``percepts`` is a list of dicts ``{"sq": [x, y], "pit": bool?, "breeze": bool?}``
    (as produced by ``load_scenarios``). This reproduces the notebook's manual
    KB assembly, e.g. the base KB is

        kb = wumpus_physics()
        kb += [-P(1,1), -B(1,1), -P(2,1), +B(2,1)]
    """
    kb = wumpus_physics()
    for p in percepts:
        x, y = p["sq"]
        if "pit" in p:
            kb.append(frozenset({Pv(x, y) if p["pit"] else -Pv(x, y)}))
        if "breeze" in p:
            kb.append(frozenset({Bv(x, y) if p["breeze"] else -Bv(x, y)}))
    return kb


def classify(kb, x, y):
    safe = entails(kb, [frozenset({-Pv(x, y)})])   # provably no pit
    deadly = entails(kb, [frozenset({Pv(x, y)})])  # provably a pit
    if safe:
        return "SAFE (proved)"
    if deadly:
        return "PIT (proved)"
    return "UNKNOWN"


# ---- 5. instance loading ----------------------------------------------------

def load_scenarios(path=None):
    """Load the provided instance bank (percept scenarios + example CNFs).

    Values are exactly those from the Session-A notebook. See instances.json.
    """
    path = Path(path or Path(__file__).with_name("instances.json"))
    return json.loads(path.read_text())
