
import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

from solution.processing.lead_metrics import calculate_lead_metrics


class TestLeadMetrics(unittest.TestCase):

    def setUp(self):
        self.success_codes = {"renewed", "feedback_captured"}

    def call(self, hour, disposition=None, connected=False):
        return {
            "initiated_at": datetime(
                2026, 10, 1, hour, 0,
                tzinfo=ZoneInfo("Asia/Kolkata"),
            ),
            "effective_disposition": disposition,
            "connected": connected,
        }

    def test_no_calls(self):
        result = calculate_lead_metrics([], self.success_codes)

        self.assertEqual(result["total_calls"], 0)
        self.assertEqual(result["connected_calls"], 0)
        self.assertIsNone(result["last_call_at"])
        self.assertIsNone(result["current_disposition"])
        self.assertFalse(result["ever_success"])

    def test_call_counts(self):
        calls = [
            self.call(10, "renewed", True),
            self.call(11, "callback_requested", False),
        ]

        result = calculate_lead_metrics(calls, self.success_codes)

        self.assertEqual(result["total_calls"], 2)
        self.assertEqual(result["connected_calls"], 1)

    def test_current_disposition(self):
        calls = [
            self.call(10, "renewed"),
            self.call(11, "callback_requested"),
            self.call(12, None),
        ]

        result = calculate_lead_metrics(calls, self.success_codes)

        self.assertEqual(
            result["current_disposition"],
            "callback_requested",
        )

    def test_latest_call_time(self):
        calls = [
            self.call(10, "renewed"),
            self.call(12, None),
        ]

        result = calculate_lead_metrics(calls, self.success_codes)

        self.assertEqual(result["last_call_at"].hour, 12)

    def test_ever_success(self):
        calls = [
            self.call(10, "renewed"),
            self.call(11, "callback_requested"),
        ]

        result = calculate_lead_metrics(calls, self.success_codes)

        self.assertTrue(result["ever_success"])


if __name__ == "__main__":
    unittest.main()
