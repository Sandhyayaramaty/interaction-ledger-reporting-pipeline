
import unittest

from solution.db import get_connection
from solution.processing.event_validator import validate_event
from solution.ingestion.events import insert_event


class TestEventInsert(unittest.TestCase):

    def test_insert_and_duplicate_event(self):
        raw_event = {
            "event_id": "evt_insert_test_001",
            "event_type": "call.initiated",
            "workflow_id": "motor_renewal",
            "call_id": "call_insert_test_001",
            "occurred_at": "2026-10-01T05:26:10Z",
            "phone": "+919876543210",
            "payload": {},
        }

        event, error = validate_event(raw_event)
        self.assertIsNone(error)

        try:
            with get_connection() as conn:
                first_insert = insert_event(
                    conn, event, "test.jsonl", 1
                )

                second_insert = insert_event(
                    conn, event, "test.jsonl", 2
                )

                self.assertTrue(first_insert)
                self.assertFalse(second_insert)

        finally:
            with get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        DELETE FROM app.interaction_events
                        WHERE event_id = %s
                        """,
                        ("evt_insert_test_001",),
                    )


if __name__ == "__main__":
    unittest.main()
