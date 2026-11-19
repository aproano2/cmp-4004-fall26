import json
import unittest

from run_arms import BASE, evaluate, parse_answer, parse_cnf, run_arm, solve


class FakeLLM:
    model = "test"

    def __init__(self, output):
        self.output = output
        self.messages = None

    def __call__(self, messages):
        self.messages = messages
        return {"raw_output": self.output}


class ArmTests(unittest.TestCase):
    def setUp(self):
        self.problems = json.loads((BASE / "problems/problems.json").read_text())
        self.truths = json.loads((BASE / "problems/ground_truth.json").read_text())

    def test_a_all_cases(self):
        for problem, truth in zip(self.problems, self.truths):
            self.assertEqual(run_arm("A", problem, truth)["status"], "correct")

    def test_partial_assignment_is_completed(self):
        answer, _ = solve([[1, 2]], 3)
        self.assertEqual(set(answer), {"1", "2", "3"})
        self.assertTrue(answer["1"] or answer["2"])

    def test_empty_formula_and_empty_clause(self):
        self.assertIsNotNone(solve(parse_cnf('{"clauses": []}', 3), 3)[0])
        self.assertIsNone(solve(parse_cnf('{"clauses": [[]]}', 3), 3)[0])

    def test_invalid_literals_and_incomplete_answers(self):
        for literal in (True, 0, 4, 1.5):
            with self.assertRaises(ValueError):
                parse_cnf(json.dumps({"clauses": [[literal]]}), 3)
        with self.assertRaises(ValueError):
            parse_answer('{"status":"SAT", "assignment":{"1":true}}', 3)

    def test_b_does_not_receive_ground_truth(self):
        client = FakeLLM('{"clauses": [[-1]]}')
        result = run_arm("B", self.problems[0], self.truths[0], client)
        self.assertEqual(result["status"], "incorrect")
        self.assertIsNone(result["error"])
        altered = dict(self.truths[0], cnf=[[1]], witness={"1": False})
        second = FakeLLM(client.output)
        run_arm("B", self.problems[0], altered, second)
        self.assertEqual(client.messages, second.messages)

    def test_parse_error_and_unsat_are_distinct(self):
        for output, status, error in (
            ("not json", "no-answer", "parse_error"),
            ('{"clauses": [[1], [-1]]}', "incorrect", "solver_unsat"),
        ):
            row = run_arm("B", self.problems[0], self.truths[0], FakeLLM(output))
            self.assertEqual(row["status"], status)
            self.assertTrue(row["error"].startswith(error))

    def test_c_and_alternative_valid_answer(self):
        truth = {"status": "SAT", "cnf": [[1, 2]]}
        for assignment in ({"1": True, "2": False}, {"1": False, "2": True}):
            self.assertEqual(evaluate(assignment, truth), "correct")
        client = FakeLLM(json.dumps({"status": "SAT", "assignment": self.truths[0]["witness"]}))
        row = run_arm("C", self.problems[0], self.truths[0], client)
        self.assertEqual(row["status"], "correct")
        self.assertEqual(row["solver_time_s"], 0)


class SequenceLLM:
    model = "test"

    def __init__(self, outputs):
        self.outputs = iter(outputs)
        self.history = []

    def __call__(self, messages):
        self.history.append(messages)
        return {"raw_output": next(self.outputs), "llm_time_s": 1.0,
                "input_tokens": 10, "output_tokens": 5}


class RefinementTests(unittest.TestCase):
    def setUp(self):
        self.problem = json.loads((BASE / "problems/problems.json").read_text())[0]
        self.truth = json.loads((BASE / "problems/ground_truth.json").read_text())[0]
        self.valid = json.dumps({"clauses": self.truth["cnf"]})

    def test_stops_after_three_refinements_and_counts_all_costs(self):
        client = SequenceLLM(["bad"] * 4)
        row = run_arm("Bp", self.problem, self.truth, client)
        self.assertEqual(len(client.history), 4)
        self.assertEqual(row["refinements"], 3)
        self.assertEqual(row["input_tokens"], 40)
        self.assertEqual(row["output_tokens"], 20)
        self.assertEqual(row["llm_time_s"], 4)
        self.assertIsNone(row["success_iteration"])

    def test_repairs_parse_error_then_unsat_without_ground_truth(self):
        outputs = ["bad", '{"clauses": [[1], [-1]]}', self.valid]
        client = SequenceLLM(outputs)
        row = run_arm("Bp", self.problem, self.truth, client)
        self.assertEqual(row["status"], "correct")
        self.assertEqual(row["success_iteration"], 2)
        self.assertIn("parse_error:", client.history[1][-1]["content"])
        self.assertIn("solver_unsat", client.history[2][-1]["content"])
        other = SequenceLLM(outputs)
        run_arm("Bp", self.problem, dict(self.truth, status="UNSAT", cnf=[[]]), other)
        self.assertEqual(client.history, other.history)

    def test_silent_error_does_not_trigger_refinement(self):
        client = SequenceLLM(['{"clauses": [[-1]]}'])
        row = run_arm("Bp", self.problem, self.truth, client)
        self.assertEqual(row["status"], "incorrect")
        self.assertEqual(row["refinements"], 0)
        self.assertIsNone(row["success_iteration"])

    def test_reuses_b_initial_attempt(self):
        client = SequenceLLM(["bad", self.valid])
        initial = run_arm("B", self.problem, self.truth, client)
        row = run_arm("Bp", self.problem, self.truth, client, initial=initial)
        self.assertEqual(len(client.history), 2)
        self.assertEqual(row["status"], "correct")
        self.assertEqual(row["input_tokens"], 20)
        self.assertEqual(row["attempts"][0]["raw_output"], initial["raw_output"])
        self.assertEqual(initial["status"], "no-answer")

    def test_no_retry_on_connection_failure(self):
        def disconnected(messages):
            raise OSError("offline")
        disconnected.model = "test"
        row = run_arm("Bp", self.problem, self.truth, disconnected)
        self.assertEqual(row["refinements"], 0)
        self.assertTrue(row["error"].startswith("llm_error:"))


if __name__ == "__main__":
    unittest.main()
