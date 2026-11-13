import unittest

from solution.processing.call_loader import load_linked_events


class TestCallLoader(unittest.TestCase):

    def test_load_linked_events(self):
        events = load_linked_events()

        self.assertGreater(len(events), 0)

        first = events[0]

        self.assertIn("event_id", first)
        self.assertIn("event_type", first)
        self.assertIn("workflow_id", first)
        self.assertIn("call_id", first)
        self.assertIn("occurred_at", first)
        self.assertIn("payload", first)
        self.assertIn("lead_id", first)

        self.assertIsNotNone(first["lead_id"])


if __name__ == "__main__":
    unittest.main()
