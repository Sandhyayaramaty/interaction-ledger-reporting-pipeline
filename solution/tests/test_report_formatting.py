import unittest

from solution.processing.encryption import encrypt_value
from solution.processing.report_formatting import mask_phone


class TestReportFormatting(unittest.TestCase):

    def test_mask_phone(self):
        encrypted = encrypt_value("+919876543210")

        result = mask_phone(encrypted)

        self.assertEqual(
            result,
            "+91******3210",
        )

        self.assertNotIn(
            "9876543210",
            result,
        )


if __name__ == "__main__":
    unittest.main()