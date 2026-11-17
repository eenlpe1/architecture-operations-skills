"""Check fixture integrity and the separation of model inputs from the rubric."""

import json
from pathlib import Path
import unittest


class ScenarioIntegrityTests(unittest.TestCase):
    def test_scenario_inputs_and_evaluator_expectations_are_separate_and_complete(self):
        directory = Path(__file__).parent / "scenarios"
        inputs = json.loads((directory / "inputs.json").read_text())["scenarios"]
        expected = json.loads((directory / "expectations.json").read_text())["scenarios"]
        input_ids = [item["id"] for item in inputs]
        expected_ids = [item["id"] for item in expected]
        self.assertEqual(len(input_ids), len(set(input_ids)), "duplicate input scenario ID")
        self.assertEqual(len(expected_ids), len(set(expected_ids)), "duplicate rubric scenario ID")
        self.assertEqual(set(input_ids), set(expected_ids), "input/rubric scenario mismatch")
        for item in inputs:
            with self.subTest(scenario=item["id"]):
                self.assertEqual(set(item), {"id", "user_request", "artifacts"})
                self.assertIsInstance(item["user_request"], str)
                self.assertTrue(item["user_request"].strip())
                self.assertIsInstance(item["artifacts"], dict)
        for item in expected:
            with self.subTest(scenario=item["id"]):
                self.assertTrue(item["route"])
                self.assertTrue(item["required_outcomes"])
                self.assertTrue(item["disallowed_outcomes"])
                for outcome in item["required_outcomes"] + item["disallowed_outcomes"]:
                    self.assertIsInstance(outcome, str)
                    self.assertTrue(outcome.strip())


if __name__ == "__main__":
    unittest.main()
