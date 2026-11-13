
import unittest

from solution.processing.event_validator import validate_event


class TestEventValidator(unittest.TestCase):

    def setUp(self):
        self.event = {
            "event_id": "evt_test_001",
            "event_type": "call.initiated",
            "workflow_id": "motor_renewal",
            "call_id": "call_test_001",
            "occurred_at": "2026-10-01T05:26:10Z",
            "phone": "+919876543210",
            "payload": {},
        }

    def test_valid_event(self):
        result, error = validate_event(self.event)

        self.assertIsNone(error)
        self.assertEqual(result["event_id"], "evt_test_001")
        self.assertIsNotNone(result["phone_lookup_hash"])
        self.assertNotIn("phone", result)

    def test_override_without_phone(self):
        event = self.event.copy()
        event["event_type"] = "disposition.override"
        event.pop("phone")

        result, error = validate_event(event)

        self.assertIsNone(error)
        self.assertIsNone(result["phone_lookup_hash"])

    def test_missing_event_id(self):
        event = self.event.copy()
        event.pop("event_id")

        result, error = validate_event(event)

        self.assertIsNone(result)
        self.assertEqual(error, "missing_required:event_id")

    def test_unsupported_phone_is_preserved(self):
        event = self.event.copy()
        event["phone"] = "+1 415 555 0134"

        result, error = validate_event(event)

        self.assertIsNone(error)
        self.assertIsNotNone(result)
        self.assertIsNone(result["phone_lookup_hash"])
        self.assertNotIn("phone", result)

    def test_unknown_event_type(self):
        event = self.event.copy()
        event["event_type"] = "call.unknown"

        result, error = validate_event(event)

        self.assertIsNone(result)
        self.assertEqual(error, "unknown_event_type")

    def test_invalid_timestamp(self):
        event = self.event.copy()
        event["occurred_at"] = "not-a-date"

        result, error = validate_event(event)

        self.assertIsNone(result)
        self.assertEqual(error, "invalid_timestamp")


if __name__ == "__main__":
    unittest.main()
