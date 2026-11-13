import csv
from pathlib import Path

from solution.processing.lead_report_builder import build_lead_report_rows
from solution.processing.report_formatting import mask_phone


from solution.paths import REPORTS_DIR

OUTPUT_DIR = REPORTS_DIR


def generate_lead_report():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    rows = build_lead_report_rows()

    output_path = OUTPUT_DIR / "lead_report.csv"

    fieldnames = [
        "workflow_id",
        "external_ref",
        "batch_id",
        "phone_masked",
        "bucket",
        "total_calls",
        "connected_calls",
        "last_call_at",
        "current_disposition",
        "ever_success",
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

        for row in rows:
            writer.writerow({
                "workflow_id": row["workflow_id"],
                "external_ref": row["external_ref"],
                "batch_id": row["batch_id"],
                "phone_masked": mask_phone(
                    row["phone_encrypted"]
                ),
                "bucket": row["bucket"],
                "total_calls": row["total_calls"],
                "connected_calls": row["connected_calls"],
                "last_call_at": (
                    row["last_call_at"].isoformat()
                    if row["last_call_at"]
                    else ""
                ),
                "current_disposition": (
                    row["current_disposition"]
                    if row["current_disposition"]
                    else ""
                ),
                "ever_success": str(row["ever_success"]).lower(),
            })

    return output_path


if __name__ == "__main__":
    path = generate_lead_report()
    print(f"Generated: {path}")