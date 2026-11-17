from types import SimpleNamespace

from arm_c import format_errors, parse_answer, prompt_for, run_problem

PROBLEM = {"id": "T1", "difficulty": "facil", "statement": "X es 1",
           "answer_format": {"keys": ["X", "Y"], "allowed_values": {"X": [1, 2], "Y": ["A", "B"]}}}
ARGS = SimpleNamespace(model="test", temperature=0.0, seed=0, timeout=1, url="http://localhost")


def test_prompt_has_only_public_fields():
    text = prompt_for(PROBLEM)
    assert "X es 1" in text and '"Y": ["A", "B"]' in text
    assert "facil" not in text


def test_parse_modes():
    assert parse_answer('{"X": 1}') == ({"X": 1}, "strict")
    assert parse_answer('```json\n{"X": 1}\n```') == ({"X": 1}, "extracted")
    assert parse_answer("no sé") == (None, "failed")


def test_format_errors_use_public_format_only():
    assert format_errors({"X": 1, "Y": "a"}, PROBLEM["answer_format"]) == []
    assert format_errors({"X": 3}, PROBLEM["answer_format"]) == ["out_of_domain:X=3", "missing:Y"]
    assert format_errors(None, PROBLEM["answer_format"]) == ["unparseable"]


def test_run_problem_single_call():
    calls = []
    def fake(messages, *args):
        calls.append(messages)
        return {"text": '{"X": 2, "Y": "B"}', "llm_s": 1.5, "tokens_in": 10, "tokens_out": 5}
    rec = run_problem(PROBLEM, ARGS, fake)
    assert len(calls) == 1 and rec["answer"] == {"X": 2, "Y": "B"}
    assert rec["solver_s"] == 0 and rec["format_errors"] == [] and rec["wall_s"] >= 1.5
