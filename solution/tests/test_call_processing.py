import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

from solution.processing.call_processing import build_call_record


class TestCallProcessing(unittest.TestCase):

    def setUp(self):
        self.valid_codes = {
            "renewed",
            "callback_requested",
        }

    def event(
        self,
        event_type,
        hour=10,
        code=None,
    ):
        event = {
            "event_id": f"evt_{event_type}_{hour}",
            "event_type": event_type,
            "workflow_id": "motor_renewal",
            "call_id": "call_001",
            "occurred_at": datetime(
                2026,
                10,
                1,
                hour,
                0,
                tzinfo=ZoneInfo("Asia/Kolkata"),
            ),
            "payload": {},
            "lead_id": 123,
        }

        if code:
            event["payload"] = {
                "disposition_code": code
            }

        return event

    def test_call_requires_initiated(self):
        events = [
            self.event("call.connected"),
            self.event("call.ended"),
        ]

        result = build_call_record(
            events,
            self.valid_codes,
        )

        self.assertIsNone(result)

    def test_connected_call(self):
        events = [
            self.event("call.initiated"),
            self.event("call.connected"),
            self.event(
                "disposition.set",
                code="renewed",
            ),
        ]

        result = build_call_record(
            events,
            self.valid_codes,
        )

        self.assertIsNotNone(result)
        self.assertTrue(result["connected"])
        self.assertFalse(result["telephony_failed"])
        self.assertEqual(
            result["effective_disposition"],
            "renewed",
        )

    def test_telephony_failed_call(self):
        events = [
            self.event("call.initiated"),
            self.event("call.telephony_failed"),
        ]

        result = build_call_record(
            events,
            self.valid_codes,
        )

        self.assertIsNotNone(result)
        self.assertFalse(result["connected"])
        self.assertTrue(result["telephony_failed"])

    def test_call_date_is_ist(self):
        events = [
            {
                **self.event("call.initiated"),
                "occurred_at": datetime(
                    2026,
                    10,
                    1,
                    18,
                    45,
                    tzinfo=ZoneInfo("UTC"),
                ),
            }
        ]

        result = build_call_record(
            events,
            self.valid_codes,
        )

        # 18:45 UTC = 00:15 IST on Oct 2
        self.assertEqual(
            result["call_date"].isoformat(),
            "2026-10-02",
        )


if __name__ == "__main__":
    unittest.main()