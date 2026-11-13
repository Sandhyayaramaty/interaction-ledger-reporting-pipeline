
import unittest

from solution.processing.schema_loader import load_schema
from solution.processing.lead_validator import validate_lead_row


class TestLeadValidator(unittest.TestCase):

    def setUp(self):
        self.schema = load_schema("motor_renewal")

    def test_valid_row(self):
        row = {
            "customer_name": "Aarav Menon",
            "phone": "+916463745499",
            "policy_number": "MOT/2026/100142",
            "policy_expiry": "21-11-2026",
            "premium_amount": "27554",
            "preferred_language": "mr",
        }

        data, rejection, warnings = validate_lead_row(
            row, self.schema
        )

        self.assertIsNone(rejection)
        self.assertEqual(data["phone"], "+916463745499")
        self.assertEqual(data["policy_expiry"], "2026-11-21")
        self.assertEqual(data["premium_amount"], "27554.00")
        self.assertEqual(warnings, [])

    def test_missing_required_phone(self):
        row = {
            "customer_name": "Aarav Menon",
            "phone": "",
            "policy_number": "MOT/2026/100142",
        }

        data, rejection, warnings = validate_lead_row(
            row, self.schema
        )

        self.assertIsNone(data)
        self.assertEqual(rejection, "missing_required:phone")

    def test_invalid_optional_date(self):
        row = {
            "customer_name": "Aarav Menon",
            "phone": "6463745499",
            "policy_number": "MOT/2026/100142",
            "policy_expiry": "not-a-date",
        }

        data, rejection, warnings = validate_lead_row(
            row, self.schema
        )

        self.assertIsNone(rejection)
        self.assertIsNone(data["policy_expiry"])
        self.assertEqual(len(warnings), 1)
        self.assertEqual(
            warnings[0]["field_name"], "policy_expiry"
        )

    def test_alias_headers(self):
        row = {
            "name": "Aarav Menon",
            "mobile": "6463745499",
            "policy": "MOT/2026/100142",
        }

        data, rejection, warnings = validate_lead_row(
            row, self.schema
        )

        self.assertIsNone(rejection)
        self.assertEqual(data["customer_name"], "Aarav Menon")
        self.assertEqual(data["phone"], "+916463745499")


if __name__ == "__main__":
    unittest.main()
