
import unittest

from solution.processing.schema_loader import load_schema
from solution.processing.lead_record import prepare_lead_record
from solution.processing.encryption import decrypt_value, hash_phone


class TestLeadRecord(unittest.TestCase):

    def test_motor_renewal_record(self):
        schema = load_schema("motor_renewal")

        data = {
            "customer_name": "Aarav Menon",
            "phone": "+916463745499",
            "policy_number": "MOT/2026/100142",
            "policy_expiry": "2026-11-21",
            "premium_amount": "27554.00",
            "preferred_language": "mr",
        }

        record = prepare_lead_record(
            data, schema, "batch_001"
        )

        self.assertEqual(record["workflow_id"], "motor_renewal")
        self.assertEqual(record["batch_id"], "batch_001")
        self.assertEqual(record["external_ref"], "MOT/2026/100142")

        self.assertEqual(
            decrypt_value(record["phone_encrypted"]),
            "+916463745499",
        )

        self.assertEqual(
            decrypt_value(record["customer_name_encrypted"]),
            "Aarav Menon",
        )

        self.assertEqual(
            record["phone_lookup_hash"],
            hash_phone("+916463745499"),
        )

        self.assertNotIn("phone", record["attributes"])
        self.assertNotIn("customer_name", record["attributes"])
        self.assertNotIn("policy_number", record["attributes"])

        self.assertEqual(
            record["attributes"]["preferred_language"], "mr"
        )

    def test_policy_feedback_record(self):
        schema = load_schema("policy_feedback")

        data = {
            "customer_name": "Rahul Shetty",
            "phone": "+916761968225",
            "order_id": "ORD-700079",
            "product": "Earbuds",
            "order_date": "2026-09-22",
            "preferred_language": "ta",
        }

        record = prepare_lead_record(
            data, schema, "batch_001"
        )

        self.assertEqual(record["external_ref"], "ORD-700079")
        self.assertEqual(record["workflow_id"], "policy_feedback")
        self.assertEqual(record["attributes"]["product"], "Earbuds")

        self.assertNotIn("phone", record["attributes"])
        self.assertNotIn("customer_name", record["attributes"])
        self.assertNotIn("order_id", record["attributes"])


if __name__ == "__main__":
    unittest.main()
