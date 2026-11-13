
import unittest

from solution.processing.workflow_codes import load_workflow_codes


class TestWorkflowCodes(unittest.TestCase):

    def test_workflow_codes_load(self):
        terminal, success = load_workflow_codes()

        self.assertIn("motor_renewal", terminal)
        self.assertIn("policy_feedback", terminal)

        self.assertIn("renewed", success["motor_renewal"])
        self.assertIn("feedback_captured", success["policy_feedback"])

        self.assertNotIn("callback_requested", success["motor_renewal"])


if __name__ == "__main__":
    unittest.main()
