
import unittest

from solution.processing.lead_report_data import load_lead_report_data


class TestLeadReportData(unittest.TestCase):

    def test_all_leads_are_included(self):
        leads = load_lead_report_data()

        self.assertEqual(len(leads), 1892)

        for lead in leads:
            self.assertIn(
                lead["bucket"],
                {
                    "yet_to_reach_out",
                    "completed",
                    "in_progress_telephony_failed",
                    "in_progress_dialed",
                },
            )

    def test_leads_without_calls_are_included(self):
        leads = load_lead_report_data()

        untouched = [
            lead for lead in leads
            if not lead["calls"]
        ]

        for lead in untouched:
            self.assertEqual(
                lead["bucket"],
                "yet_to_reach_out",
            )


if __name__ == "__main__":
    unittest.main()
