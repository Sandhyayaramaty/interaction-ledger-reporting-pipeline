import csv
from collections import defaultdict
from pathlib import Path

from solution.processing.lead_report_builder import build_lead_report_rows


from solution.paths import REPORTS_DIR

OUTPUT_DIR = REPORTS_DIR


def generate_batch_summary():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    leads = build_lead_report_rows()

    grouped = defaultdict(list)

    for lead in leads:
        grouped[
            (lead["workflow_id"], lead["batch_id"])
        ].append(lead)

    rows = []

    for (workflow_id, batch_id), batch_leads in grouped.items():

        counts = {
            "yet_to_reach_out": 0,
            "in_progress_telephony_failed": 0,
            "in_progress_dialed": 0,
            "completed": 0,
        }

        for lead in batch_leads:
            counts[lead["bucket"]] += 1

        rows.append({
            "workflow_id": workflow_id,
            "batch_id": batch_id,
            "total_leads": len(batch_leads),
            "yet_to_reach_out": counts["yet_to_reach_out"],
            "in_progress_telephony_failed": (
                counts["in_progress_telephony_failed"]
            ),
            "in_progress_dialed": counts["in_progress_dialed"],
            "completed": counts["completed"],
        })

    rows.sort(
        key=lambda row: (
            row["workflow_id"],
            row["batch_id"],
        )
    )

    output_path = OUTPUT_DIR / "batch_summary.csv"

    fieldnames = [
        "workflow_id",
        "batch_id",
        "total_leads",
        "yet_to_reach_out",
        "in_progress_telephony_failed",
        "in_progress_dialed",
        "completed",
    ]

    with output_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(rows)

    return output_path


if __name__ == "__main__":
    path = generate_batch_summary()
    print(f"Generated: {path}")