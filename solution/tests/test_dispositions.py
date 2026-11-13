
import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

from solution.processing.dispositions import get_effective_disposition


class TestEffectiveDisposition(unittest.TestCase):

    def setUp(self):
        self.valid_codes = {
            "renewed",
            "callback_requested",
            "payment_link_sent",
        }

    def event(self, event_type, code, hour):
        return {
            "event_type": event_type,
            "occurred_at": datetime(
                2026, 10, 1, hour, 0,
                tzinfo=ZoneInfo("Asia/Kolkata"),
            ),
            "payload": {"disposition_code": code},
        }

    def test_latest_set_wins(self):
        events = [
            self.event("disposition.set", "callback_requested", 10),
            self.event("disposition.set", "payment_link_sent", 11),
        ]

        result = get_effective_disposition(
            events, self.valid_codes
        )

        self.assertEqual(result, "payment_link_sent")

    def test_override_takes_priority(self):
        events = [
            self.event("disposition.set", "payment_link_sent", 11),
            self.event("disposition.override", "renewed", 10),
        ]

        result = get_effective_disposition(
            events, self.valid_codes
        )

        self.assertEqual(result, "renewed")

    def test_latest_override_wins(self):
        events = [
            self.event("disposition.override", "renewed", 10),
            self.event(
                "disposition.override",
                "callback_requested",
                12,
            ),
        ]

        result = get_effective_disposition(
            events, self.valid_codes
        )

        self.assertEqual(result, "callback_requested")

    def test_unknown_disposition_is_ignored(self):
        events = [
            self.event("disposition.set", "renewed", 10),
            self.event("disposition.override", "unknown", 12),
        ]

        result = get_effective_disposition(
            events, self.valid_codes
        )

        self.assertEqual(result, "renewed")

    def test_no_valid_disposition(self):
        events = [
            self.event("disposition.set", "unknown", 10),
        ]

        result = get_effective_disposition(
            events, self.valid_codes
        )

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
