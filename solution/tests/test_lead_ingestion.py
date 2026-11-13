
import unittest

from solution.ingestion.lead_ingestion import ingest_lead_file


class TestLeadIngestion(unittest.TestCase):

    def test_ingest_motor_batch_001(self):
        result = ingest_lead_file(
            "data/drop_1/leads/motor_renewal/batch_001.csv",
            "motor_renewal",
        )

        print("\nIngestion metrics:", result)

        self.assertGreater(result["total_rows"], 0)
        self.assertEqual(
            result["total_rows"],
            result["accepted_rows"] + result["rejected_rows"],
        )


if __name__ == "__main__":
    unittest.main()
