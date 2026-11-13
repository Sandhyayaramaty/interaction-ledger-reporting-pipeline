
import unittest

from solution.db import get_connection
from solution.processing.schema_loader import load_schema
from solution.processing.lead_record import prepare_lead_record
from solution.processing.encryption import hash_phone, decrypt_value
from solution.ingestion.leads import upsert_lead


class TestLeadUpsert(unittest.TestCase):

    def test_insert_and_duplicate_merge(self):
        schema = load_schema("motor_renewal")
        phone = "+919876543210"

        try:
            with get_connection() as conn:
                with conn.cursor() as cursor:
                    # Clean up this test identity before starting.
                    cursor.execute(
                        """
                        DELETE FROM app.leads
                        WHERE workflow_id = %s
                        AND phone_lookup_hash = %s
                        """,
                        ("motor_renewal", hash_phone(phone)),
                    )

                first_data = {
                    "customer_name": "Test Customer",
                    "phone": phone,
                    "policy_number": "TEST-POLICY-001",
                    "policy_expiry": None,
                    "premium_amount": "5000.00",
                    "preferred_language": None,
                }

                first_record = prepare_lead_record(
                    first_data, schema, "batch_001"
                )

                first_id = upsert_lead(conn, first_record)

                second_data = {
                    "customer_name": "Updated Customer",
                    "phone": phone,
                    "policy_number": "TEST-POLICY-002",
                    "policy_expiry": "2026-12-31",
                    "premium_amount": None,
                    "preferred_language": "en",
                }

                second_record = prepare_lead_record(
                    second_data, schema, "batch_002"
                )

                second_id = upsert_lead(conn, second_record)

                self.assertEqual(first_id, second_id)

                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT batch_id, external_ref,
                               customer_name_encrypted, attributes
                        FROM app.leads
                        WHERE lead_id = %s
                        """,
                        (first_id,),
                    )

                    row = cursor.fetchone()

                self.assertEqual(row[0], "batch_001")
                self.assertEqual(row[1], "TEST-POLICY-002")
                self.assertEqual(
                    decrypt_value(row[2]), "Updated Customer"
                )
                self.assertEqual(row[3]["premium_amount"], "5000.00")
                self.assertEqual(row[3]["policy_expiry"], "2026-12-31")
                self.assertEqual(row[3]["preferred_language"], "en")

                # Clean up the test record.
                with conn.cursor() as cursor:
                    cursor.execute(
                        "DELETE FROM app.leads WHERE lead_id = %s",
                        (first_id,),
                    )

        finally:
            # The test uses a dedicated phone identity.
            pass


if __name__ == "__main__":
    unittest.main()
