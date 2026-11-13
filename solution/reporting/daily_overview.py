import csv
from collections import defaultdict
from pathlib import Path

from solution.processing.call_builder import build_all_call_records
from solution.processing.workflow_codes import load_workflow_codes


from solution.paths import REPORTS_DIR

OUTPUT_DIR = REPORTS_DIR


def generate_daily_overview():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    calls = build_all_call_records()
    _, success_codes = load_workflow_codes()

    grouped = defaultdict(list)

    for call in calls:
        grouped[
            (
                call["workflow_id"],
                call["call_date"],
            )
        ].append(call)

    rows = []

    for (workflow_id, call_date), day_calls in grouped.items():

        total_calls = len(day_calls)

        connected_calls = sum(
            1
            for call in day_calls
            if call["connected"]
        )

        success_leads = {
            call["lead_id"]
            for call in day_calls
            if call["effective_disposition"]
            in success_codes[workflow_id]
        }

        connectivity_rate = (
            connected_calls / total_calls
            if total_calls
            else 0
        )

        rows.append({
            "workflow_id": workflow_id,
            "date": call_date.isoformat(),
            "total_calls": total_calls,
            "connected_calls": connected_calls,
            "connectivity_rate": (
                f"{connectivity_rate:.4f}"
            ),
            "success_leads": len(success_leads),
        })

    rows.sort(
        key=lambda row: (
            row["workflow_id"],
            row["date"],
        )
    )

    output_path = OUTPUT_DIR / "daily_overview.csv"

    fieldnames = [
        "workflow_id",
        "date",
        "total_calls",
        "connected_calls",
        "connectivity_rate",
        "success_leads",
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
    path = generate_daily_overview()
    print(f"Generated: {path}")