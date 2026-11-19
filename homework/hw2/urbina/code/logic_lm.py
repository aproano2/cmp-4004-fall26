"""Week 6 studio — the Logic-LM arm-B plumbing (GIVEN; use it, do not rewrite).

The instructor provides the plumbing so you can spend the 25 minutes on the
*prompt* and the *refinement loop*, not on parsing. This module has:

  * ``MODEL_PROMPT``      — the exact translation prompt from the lesson plan.
  * ``parse_json(text)``  — pull the first JSON object out of an LLM reply.
  * ``build_csp(spec)``   — turn the parsed JSON spec into a CSP that the SAME
                            ``backtrack_search`` from ``csp.py`` can solve. It
                            supports the three constraint types the prompt asks
                            for: ``alldiff``, ``neq``, ``eq``.
  * ``classify_arm_b(...)`` — the four-way failure taxonomy from the plan.
  * ``EXAMPLE_PUZZLES``   — the three worked NL-puzzle → JSON-spec pairs kept inline
                            as few-shot fuel (also the first three in the bank).
  * ``load_puzzles()``    — the full bank of 20 verified puzzles from ``puzzles.json``.
  * ``worked_examples()`` — the 5 fully-worked starters (``worked_example: true``).

What you write (in ``starter.py``): the prompt wiring around your local model and
the self-refinement loop. See README §"Task 2".

Note on data: the plan's bank of *20* natural-language logic puzzles now ships as
``puzzles.json`` next to this file — each entry has the NL statement, the CSP spec
in the schema below, and the UNIQUE gold answer, all verified sound by
``_verify_puzzles.py``. Five are marked ``worked_example`` (the three inline
``EXAMPLE_PUZZLES`` plus two more); the rest are for the students to run. Load them
with ``load_puzzles()`` and report how many you ran on the scorecard.
"""
import json
import re
from pathlib import Path

from csp import backtrack_search

PUZZLE_BANK = Path(__file__).with_name("puzzles.json")


# The exact prompt from week-06.md §"Task 2 — The three-arm experiment".
MODEL_PROMPT = """Translate this logic puzzle into a CSP in the JSON format below.
Do not solve it. Output only JSON.

{{"variables": {{"name": ["domain", "values"]}},
  "constraints": [{{"type": "alldiff", "vars": [...]}},
                  {{"type": "neq", "a": "X", "b": "Y"}},
                  {{"type": "eq",  "a": "X", "b": "value"}}]}}

Puzzle:
{puzzle}"""


class ParseError(Exception):
    """Raised when an LLM reply has no recoverable JSON object."""


class ModelError(Exception):
    """Raised when JSON parses but is not a well-formed CSP spec (wrong model)."""


def parse_json(text):
    """Extract the first balanced ``{...}`` object from an LLM reply and load it.

    Local models wrap JSON in prose or ```json fences. This is deliberately
    forgiving about the wrapper and strict about the payload -- a payload that is
    not valid JSON raises ParseError (that becomes the 'malformed JSON' bucket).
    """
    if text is None:
        raise ParseError("empty reply")
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    candidate = fenced.group(1) if fenced else None
    if candidate is None:
        start = text.find("{")
        if start == -1:
            raise ParseError("no '{' in reply")
        depth = 0
        for i in range(start, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    candidate = text[start:i + 1]
                    break
        if candidate is None:
            raise ParseError("unbalanced braces")
    try:
        return json.loads(candidate)
    except json.JSONDecodeError as e:
        raise ParseError(f"invalid JSON: {e}") from e


class _SpecCSP:
    """A CSP built from a parsed spec. Same interface backtrack_search needs:
    ``variables``, ``domains``, ``neighbors``, ``consistent``, ``degree``.

    Unlike the notebook's all-different-only CSP, this evaluates the general
    alldiff / neq / eq constraint list, so the LLM's translation can be solved by
    the exact same search loop."""

    def __init__(self, variables, domains, constraints):
        self.variables = list(variables)
        self.domains = {v: set(domains[v]) for v in variables}
        self.constraints = constraints
        self.neighbors = {v: set() for v in variables}
        self._binary = []          # (a, b, kind)  kind in {"neq"}
        varset = set(variables)
        for con in constraints:
            t = con.get("type")
            if t == "alldiff":
                vs = con["vars"]
                for i, a in enumerate(vs):
                    for b in vs[i + 1:]:
                        self._link(a, b)
                        self._binary.append((a, b, "neq"))
            elif t == "neq":
                a, b = con["a"], con["b"]
                if a in varset and b in varset:
                    self._link(a, b)              # binary: two variables differ
                    self._binary.append((a, b, "neq"))
                elif a in varset:
                    self.domains[a].discard(b)    # unary: X != value
                else:
                    raise ModelError(f"neq references unknown variable: {a}")
            elif t == "eq":
                # unary pin: X == value  -> collapse the domain now
                a, val = con["a"], con["b"]
                if a not in varset:
                    raise ModelError(f"eq references unknown variable: {a}")
                
                # La intersección conserva una contradicción entre dos pistas sobre la misma variable.
                self.domains[a].intersection_update({val})
            else:
                raise ModelError(f"unknown constraint type {t!r}")

    def _link(self, a, b):
        if a not in self.neighbors or b not in self.neighbors:
            raise ModelError(f"constraint references unknown variable: {a} / {b}")
        self.neighbors[a].add(b)
        self.neighbors[b].add(a)

    def consistent(self, var, value, assignment):
        for (a, b, kind) in self._binary:
            if kind != "neq":
                continue
            if var == a and b in assignment and assignment[b] == value:
                return False
            if var == b and a in assignment and assignment[a] == value:
                return False
        return True

    def degree(self, var):
        return len(self.neighbors[var])


def build_csp(spec):
    """Validate a parsed spec and build a solvable CSP. Raises ModelError on a
    structurally invalid spec (that becomes the 'valid JSON but wrong model'
    bucket when the shape is off, before the solver ever runs)."""
    if not isinstance(spec, dict) or "variables" not in spec:
        raise ModelError("spec missing 'variables'")
    variables = spec["variables"]
    if not isinstance(variables, dict) or not variables:
        raise ModelError("'variables' must be a non-empty object")
    domains = {}
    for name, dom in variables.items():
        if not isinstance(dom, list) or not dom:
            raise ModelError(f"variable {name!r} has an empty/invalid domain")
        domains[name] = list(dom)
    constraints = spec.get("constraints", [])
    if not isinstance(constraints, list):
        raise ModelError("'constraints' must be a list")
    return _SpecCSP(list(variables), domains, constraints)


# The four-way taxonomy required by the plan for arm B.
MALFORMED = "malformed_json"          # reply did not parse as JSON
WRONG_MODEL = "valid_json_wrong_model"  # solved, but not the puzzle's answer
NO_SOLUTION = "valid_no_solution"     # over-constrained: solver returns None
TIMEOUT = "timeout"                   # solver hit its call limit
OK = "correct"                        # solver's answer matches the gold answer


def classify_arm_b(reply, gold=None, limit=200_000):
    """Run the full arm-B pipeline on one LLM reply and label the outcome.

    reply : the raw model text (should contain the CSP JSON).
    gold  : optional dict of the puzzle's correct answer {var: value}. If given,
            a solved-but-mismatching answer is labelled WRONG_MODEL.
    Returns (category, solution_or_None).
    """
    try:
        spec = parse_json(reply)
    except ParseError:
        return MALFORMED, None
    try:
        csp = build_csp(spec)
    except ModelError:
        return MALFORMED, None       # structurally broken spec == unusable model
    sol, counter = backtrack_search(csp, use_fc=True, use_mrv=True, limit=limit)
    if sol == "TIMEOUT":
        return TIMEOUT, None
    if sol is None:
        return NO_SOLUTION, None     # over-constrained: a translation error
    if gold is not None and any(sol.get(k) != v for k, v in gold.items()):
        return WRONG_MODEL, sol
    return OK, sol


# ---- worked examples (few-shot fuel; extend for the full run) ----------------
# Each entry: the NL puzzle, a correct JSON spec (as the LLM should emit it), and
# the gold answer. Use them to sanity-check build_csp and to seed your prompt.
EXAMPLE_PUZZLES = [
    {
        "puzzle": (
            "Three friends -- Ana, Bob, Cara -- each pick a different colour "
            "from red, green, blue. Ana is not red. Bob is blue."
        ),
        "spec": {
            "variables": {"Ana": ["red", "green", "blue"],
                          "Bob": ["red", "green", "blue"],
                          "Cara": ["red", "green", "blue"]},
            "constraints": [
                {"type": "alldiff", "vars": ["Ana", "Bob", "Cara"]},
                {"type": "eq", "a": "Bob", "b": "blue"},
                {"type": "neq", "a": "Ana", "b": "red"},
            ],
        },
        "gold": {"Ana": "green", "Bob": "blue", "Cara": "red"},
    },
    {
        "puzzle": (
            "Two houses, numbered 1 and 2, one owned by Xu and one by Yara. "
            "Xu does not live in house 1."
        ),
        "spec": {
            "variables": {"Xu": [1, 2], "Yara": [1, 2]},
            "constraints": [
                {"type": "alldiff", "vars": ["Xu", "Yara"]},
                {"type": "neq", "a": "Xu", "b": 1},
            ],
        },
        "gold": {"Xu": 2, "Yara": 1},
    },
    {
        "puzzle": (
            "Three tasks A, B, C run in slots 1, 2, 3 (all different). "
            "A runs in slot 1. C does not run in slot 2."
        ),
        "spec": {
            "variables": {"A": [1, 2, 3], "B": [1, 2, 3], "C": [1, 2, 3]},
            "constraints": [
                {"type": "alldiff", "vars": ["A", "B", "C"]},
                {"type": "eq", "a": "A", "b": 1},
                {"type": "neq", "a": "C", "b": 2},
            ],
        },
        "gold": {"A": 1, "B": 2, "C": 3},
    },
]


# ---- the full 20-puzzle bank -------------------------------------------------
def load_puzzles(path=None):
    """Return the list of 20 verified puzzles from ``puzzles.json``.

    Each puzzle is a dict with ``id``, ``worked_example`` (bool), ``puzzle`` (the
    NL statement), ``spec`` (a CSP spec ``build_csp`` accepts), and ``gold`` (the
    unique answer). This is the bank the three-arm experiment runs over."""
    p = Path(path) if path else PUZZLE_BANK
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)["puzzles"]


def worked_examples(path=None):
    """The 5 fully-worked starter puzzles (``worked_example: true``) -- few-shot
    fuel and the ones the plan calls out as provided examples."""
    return [p for p in load_puzzles(path) if p.get("worked_example")]
