import unittest

from solution.processing.call_builder import build_all_call_records


class TestCallBuilder(unittest.TestCase):

    def test_build_all_call_records(self):
        records = build_all_call_records()

        self.assertGreater(len(records), 0)

        first = records[0]

        self.assertIn("call_id", first)
        self.assertIn("lead_id", first)
        self.assertIn("workflow_id", first)
        self.assertIn("initiated_at", first)
        self.assertIn("call_date", first)
        self.assertIn("connected", first)
        self.assertIn("telephony_failed", first)
        self.assertIn("effective_disposition", first)

        self.assertIsNotNone(first["lead_id"])


if __name__ == "__main__":
    unittest.main()
