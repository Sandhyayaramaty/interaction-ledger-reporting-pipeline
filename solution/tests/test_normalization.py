
import unittest

from solution.processing.normalization import (
    NormalizationError,
    normalize_header,
    build_header_map,
    normalize_phone,
    normalize_date,
    normalize_decimal,
    normalize_enum,
    normalize_field,
)


class TestNormalization(unittest.TestCase):

    def test_phone_formats(self):
        self.assertEqual(
            normalize_phone("91-77187-50036"),
            "+917718750036",
        )
        self.assertEqual(
            normalize_phone("07932896340"),
            "+917932896340",
        )
        self.assertEqual(
            normalize_phone("+91 6463745499"),
            "+916463745499",
        )

    def test_invalid_phone(self):
        with self.assertRaises(NormalizationError):
            normalize_phone("12345")

    def test_date_formats(self):
        self.assertEqual(normalize_date("2026-11-21"), "2026-11-21")
        self.assertEqual(normalize_date("21/11/2026"), "2026-11-21")
        self.assertEqual(normalize_date("21-11-2026"), "2026-11-21")
        self.assertEqual(normalize_date("21-Nov-2026"), "2026-11-21")

    def test_invalid_date(self):
        with self.assertRaises(NormalizationError):
            normalize_date("31-02-2026")

    def test_decimal_formats(self):
        self.assertEqual(normalize_decimal("₹27,554"), "27554.00")
        self.assertEqual(normalize_decimal("Rs. 6,850"), "6850.00")
        self.assertEqual(normalize_decimal("INR 1250.5"), "1250.50")

    def test_invalid_decimal(self):
        with self.assertRaises(NormalizationError):
            normalize_decimal("-500")

    def test_enum(self):
        self.assertEqual(
            normalize_enum("MR", ["en", "hi", "mr"]),
            "mr",
        )

    def test_invalid_enum(self):
        with self.assertRaises(NormalizationError):
            normalize_enum("fr", ["en", "hi", "mr"])

    def test_header_aliases(self):
        fields = [
            {
                "name": "customer_name",
                "aliases": ["name", "customer name"],
            },
            {
                "name": "phone",
                "aliases": ["mobile", "phone number"],
            },
        ]

        mapping = build_header_map(fields)

        self.assertEqual(mapping["customer name"], "customer_name")
        self.assertEqual(mapping["mobile"], "phone")
        self.assertEqual(normalize_header(" Customer_Name "), "customer name")

    def test_missing_optional_value(self):
        field = {
            "name": "policy_expiry",
            "type": "date",
        }

        self.assertIsNone(normalize_field(field, ""))


if __name__ == "__main__":
    unittest.main()
