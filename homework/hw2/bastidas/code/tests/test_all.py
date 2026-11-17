"""Tests del duelo 2. Correr desde la carpeta del deber:  python -m pytest code/tests -q"""
import copy
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))

from arms import FEEDBACK, run_arm_a, run_arm_b, run_arm_c        # noqa: E402
from csp_solver import CSP, solve                                 # noqa: E402
from llm import LLM                                               # noqa: E402
from spec import (ParseError, SchemaError, ScopeError, build_csp,  # noqa: E402
                  match_names, parse_answer_json, parse_spec_json)
from taxonomy import classify                                     # noqa: E402
from verify_problems import brute_force                           # noqa: E402

PROBLEMS = json.loads((HERE.parent / "problems" / "problems.json").read_text())["problems"]
P = {p["id"]: p for p in PROBLEMS}


def fake(*replies):
    return LLM("fake", script=list(replies))


def spec_text(spec):
    return "```json\n" + json.dumps(spec) + "\n```"


# ------------------------------------------------------------- banco --
def test_bank_has_40_problems_in_4_levels():
    assert len(PROBLEMS) == 40
    assert sorted({p["level"] for p in PROBLEMS}) == [1, 2, 3, 4]
    assert all(sum(p["level"] == lv for p in PROBLEMS) == 10 for lv in range(1, 5))


def test_ground_truth_unique_by_brute_force_level1_and_2():
    for p in PROBLEMS[:20]:
        sols = brute_force(p)
        assert sols == [p["gold"]], p["id"]


def test_arm_a_solves_everything():
    assert all(run_arm_a(p)["outcome"] == "correct" for p in PROBLEMS)


# ------------------------------------------------------------- solver --
def test_solver_finds_unique_and_counts_two():
    csp = CSP(["x", "y"], {"x": [1, 2], "y": [1, 2]})
    csp.add_alldiff(["x", "y"])
    assert len(solve(csp, max_solutions=5)["solutions"]) == 2
    csp.add_unary("x", lambda v: v == 1)
    assert solve(csp, max_solutions=5)["solutions"] == [{"x": 1, "y": 2}]


def test_solver_proves_unsat():
    csp = CSP(["x", "y"], {"x": [1], "y": [1]})
    csp.add_alldiff(["x", "y"])
    res = solve(csp)
    assert res["status"] == "ok" and res["solutions"] == []


def test_solver_timeout():
    vs = [f"v{i}" for i in range(9)]
    csp = CSP(vs, {v: list(range(8)) for v in vs})
    csp.add_alldiff(vs)                              # pigeonhole: 9 en 8 casillas
    res = solve(csp, limit=500, use_fc=False, use_mrv=False)
    assert res["status"] == "timeout"


# ------------------------------------------------------------- parser --
def test_parse_tolerates_prose_and_fences():
    s = parse_spec_json('Sure!\n```json\n{"variables": {"a": [1]}}\n```\nDone.')
    assert s == {"variables": {"a": [1]}}


def test_parse_errors():
    for bad in ["", "no json here", '{"variables": {"a": [1,]}}', '{"variables": {']:
        try:
            parse_spec_json(bad)
            assert False, bad
        except ParseError:
            pass


def test_answer_parser_takes_last_object():
    assert parse_answer_json('first {"a": 1} then {"a": 2}') == {"a": 2}


def test_schema_and_scope_errors():
    cases = [({"vars": {}}, SchemaError),
             ({"variables": {"a": 3}}, SchemaError),
             ({"variables": {"a": [1, 2]}, "constraints": [{"type": "below", "a": "a", "b": 1}]}, SchemaError),
             ({"variables": {"a": [1, 2]}, "constraints": [{"type": "offset", "a": "a", "b": "a"}]}, SchemaError),
             ({"variables": {"a": [1, 2]}, "constraints": [{"type": "eq", "a": "z", "b": 1}]}, ScopeError),
             ({"variables": {"a": [1, 2]}, "constraints": [{"type": "eq", "a": "a", "b": "red"}]}, ScopeError),
             ({"variables": {"a": [1, 2]}, "constraints": [{"type": "alldiff", "vars": ["a"]}]}, ScopeError)]
    for spec, err in cases:
        try:
            build_csp(spec)
            assert False, spec
        except err:
            pass


def test_name_matching_is_tolerant_but_not_ambiguous():
    m = match_names(["Ana", "red", "cat"], ["ana", "red_house", "Cat", "catalog"])
    assert m == {"Ana": "ana", "red": "red_house", "cat": "Cat"}
    assert match_names(["red"], ["red_house", "red_door"]) == {"red": None}


# ------------------------------------------------------------- brazos --
def test_arm_b_correct_first_try():
    p = P["L2-01"]
    rb, rp, att = run_arm_b(fake(spec_text(p["spec"])), p)
    assert rb["outcome"] == rp["outcome"] == "correct" and rp["iterations"] == 0


def test_refinement_feeds_back_only_solver_errors_and_recovers():
    p = P["L2-01"]
    model = fake("not json at all", spec_text(p["spec"]))
    rb, rp, att = run_arm_b(model, p)
    assert rb["outcome"] == "no_answer" and rb["signal"] == "parse"
    assert rp["outcome"] == "correct" and rp["iterations"] == 1


def test_refinement_stops_on_a_wrong_solution():
    """Sin fuga de la verdad: si el solver devuelve una solución (aunque sea mala),
    B′ se detiene; no hay ronda extra."""
    p = P["L2-01"]
    wrong = copy.deepcopy(p["spec"])
    wrong["constraints"] = wrong["constraints"][:2]          # solo alldiffs
    rb, rp, att = run_arm_b(fake(spec_text(wrong), spec_text(p["spec"])), p)
    assert rp["iterations"] == 0 and rp["outcome"] in ("incorrect", "correct")


def test_feedback_messages_never_contain_gold():
    p = P["L4-06"]
    gold_vals = json.dumps(p["gold"])
    for msg in FEEDBACK.values():
        assert gold_vals not in msg and "correct answer" not in msg.lower()


def test_refinement_max_three_rounds():
    p = P["L1-01"]
    rb, rp, att = run_arm_b(fake("x", "x", "x", "x", "x"), p)
    assert rp["iterations"] == 3 and len(att) == 4 and rp["outcome"] == "no_answer"


def test_arm_c_grading():
    p = P["L1-01"]
    good = "reasoning...\n" + json.dumps(p["gold"])
    assert run_arm_c(fake(good), p)[0]["outcome"] == "correct"
    wrong = {k: (v % 4) + 1 for k, v in p["gold"].items()}
    row = run_arm_c(fake(json.dumps(wrong)), p)[0]
    assert row["outcome"] == "incorrect" and row["detectable"] is False
    assert run_arm_c(fake("I think Ben is first."), p)[0]["outcome"] == "no_answer"


# ------------------------------------------------------------- taxonomía --
def _attempt(p, spec):
    from arms import evaluate_spec_reply
    a = evaluate_spec_reply(spec_text(spec), p)
    return a


def test_taxonomy_categories():
    p = P["L2-04"]
    # over-constrained: una pista inventada que contradice a la verdad
    s = copy.deepcopy(p["spec"])
    g = p["gold"]
    some = next(iter(g))
    s["constraints"].append({"type": "neq", "a": some, "b": g[some]})
    assert classify(_attempt(p, s), p)[0] == "over_constrained"
    # scope: alldiff que mezcla dueños y colores
    s = copy.deepcopy(p["spec"])
    s["constraints"][0]["vars"] = s["constraints"][0]["vars"] + s["constraints"][1]["vars"][:1]
    cat, info = classify(_attempt(p, s), p)
    assert cat == "scope_arity"
    # under-constrained: se borran las pistas
    s = copy.deepcopy(p["spec"])
    s["constraints"] = s["constraints"][:2]
    a = _attempt(p, s)
    if not a["correct"]:
        assert classify(a, p)[0] == "under_constrained"
    # malformed
    from arms import evaluate_spec_reply
    assert classify(evaluate_spec_reply("{oops", p), p)[0] == "malformed_syntax"


def test_reversed_offset_is_detected_as_cause():
    p = P["L1-02"]
    s = copy.deepcopy(p["spec"])
    for c in s["constraints"]:
        if c["type"] == "offset":
            c["k"] = -c["k"]
    cat, info = classify(_attempt(p, s), p)
    assert info["reversed"]
