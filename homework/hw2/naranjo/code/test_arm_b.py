import json
from types import SimpleNamespace

from arm_b import prompt_for, record, run_problem, run_solver

PROBLEM = {"id": "T1", "difficulty": "facil", "statement": "X es 1",
           "answer_format": {"keys": ["X"], "allowed_values": {"X": [1, 2]}}}
ARGS = SimpleNamespace(model="test", temperature=0.0, seed=0, timeout=1, url="http://localhost")


def test_prompt_and_solver():
    assert '"X": [1, 2]' in prompt_for(PROBLEM)
    assert run_solver("not json")["solver_status"] == "spec_error"
    spec = {"variables": {"X": [1, 2]}, "constraints": [{"expr": "X == 1"}]}
    assert run_solver(json.dumps(spec))["answer"] == {"X": 1}


def test_paired_refinement_and_feedback():
    calls = []
    def fake(messages, *args):
        calls.append(messages)
        text = "bad json" if len(calls) == 1 else '{"variables":{"X":[1]},"constraints":[]}'
        return {"text": text, "llm_s": 2, "tokens_in": 3, "tokens_out": 4}
    attempts = run_problem(PROBLEM, ARGS, fake)
    assert len(attempts) == 2
    assert calls[1][-1]["content"].startswith("JSONDecodeError:")
    assert record(PROBLEM, "B", attempts[:1], ARGS)["attempts"] == 1
    assert record(PROBLEM, "B'", attempts, ARGS)["tokens_in"] == 6


def test_three_retries_max():
    def fake(*args):
        return {"text": "bad", "llm_s": 1, "tokens_in": 1, "tokens_out": 1}
    assert len(run_problem(PROBLEM, ARGS, fake)) == 4


def test_multiple_is_not_refined():
    def fake(*args):
        return {"text": '{"variables":{"X":[1,2]},"constraints":[]}',
                "llm_s": 1, "tokens_in": 1, "tokens_out": 1}
    attempts = run_problem(PROBLEM, ARGS, fake)
    assert len(attempts) == 1
    assert attempts[0]["solver_status"] == "multiple"
