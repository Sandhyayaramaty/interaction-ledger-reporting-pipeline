
import csv
from pathlib import Path

from solution.db import get_connection

from solution.paths import REPORTS_DIR

OUTPUT_DIR = REPORTS_DIR


def generate_rejections():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT
                    workflow_id,
                    batch_id,
                    row_number,
                    reason
                FROM app.lead_rejections
                ORDER BY workflow_id, batch_id, row_number
            """)

            rows = cursor.fetchall()

    fieldnames = [
        "workflow_id",
        "batch_id",
        "row_number",
        "reason",
    ]

    output_path = OUTPUT_DIR / "rejections.csv"

    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(fieldnames)
        writer.writerows(rows)

    return output_path


if __name__ == "__main__":
    path = generate_rejections()
    print(f"Generated: {path}")
