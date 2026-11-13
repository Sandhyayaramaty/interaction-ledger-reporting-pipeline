import unittest

from solution.processing.lead_report_builder import build_lead_report_rows


class TestLeadReportBuilder(unittest.TestCase):

    def test_build_lead_report_rows(self):
        rows = build_lead_report_rows()

        self.assertEqual(len(rows), 1892)

        first = rows[0]

        required_fields = {
            "workflow_id",
            "external_ref",
            "batch_id",
            "phone_encrypted",
            "bucket",
            "total_calls",
            "connected_calls",
            "last_call_at",
            "current_disposition",
            "ever_success",
        }

        self.assertTrue(
            required_fields.issubset(first.keys())
        )

    def test_sorting(self):
        rows = build_lead_report_rows()

        keys = [
            (row["workflow_id"], row["external_ref"])
            for row in rows
        ]

        self.assertEqual(keys, sorted(keys))


if __name__ == "__main__":
    unittest.main()