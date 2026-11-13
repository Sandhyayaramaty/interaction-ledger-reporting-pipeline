
import unittest

from solution.processing.lead_bucketing import get_lead_bucket


class TestLeadBucketing(unittest.TestCase):

    def setUp(self):
        self.terminal_codes = {
            "renewed",
            "not_interested",
            "feedback_captured",
            "refused",
            "wrong_number",
            "dnd",
            "already_renewed_elsewhere",
        }

    def test_no_calls(self):
        self.assertEqual(
            get_lead_bucket([], self.terminal_codes),
            "yet_to_reach_out",
        )

    def test_completed_lead(self):
        calls = [
            {
                "telephony_failed": False,
                "effective_disposition": "renewed",
            }
        ]

        self.assertEqual(
            get_lead_bucket(calls, self.terminal_codes),
            "completed",
        )

    def test_all_calls_telephony_failed(self):
        calls = [
            {
                "telephony_failed": True,
                "effective_disposition": None,
            },
            {
                "telephony_failed": True,
                "effective_disposition": None,
            },
        ]

        self.assertEqual(
            get_lead_bucket(calls, self.terminal_codes),
            "in_progress_telephony_failed",
        )

    def test_mixed_calls(self):
        calls = [
            {
                "telephony_failed": True,
                "effective_disposition": None,
            },
            {
                "telephony_failed": False,
                "effective_disposition": None,
            },
        ]

        self.assertEqual(
            get_lead_bucket(calls, self.terminal_codes),
            "in_progress_dialed",
        )

    def test_terminal_disposition_takes_priority(self):
        calls = [
            {
                "telephony_failed": True,
                "effective_disposition": "renewed",
            }
        ]

        self.assertEqual(
            get_lead_bucket(calls, self.terminal_codes),
            "completed",
        )


if __name__ == "__main__":
    unittest.main()
