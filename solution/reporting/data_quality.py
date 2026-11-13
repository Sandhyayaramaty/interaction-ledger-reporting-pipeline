
import json
from pathlib import Path

from solution.db import get_connection

from solution.paths import DATA_DIR, REPORTS_DIR

OUTPUT_DIR = REPORTS_DIR


def get_source_event_metrics():
    """Count source event lines, malformed records and duplicate IDs."""
    total = 0
    malformed = 0
    seen_event_ids = set()
    duplicates = 0

    event_files = sorted(DATA_DIR.glob("drop_*/events/*.jsonl"))

    for event_file in event_files:
        with event_file.open("r", encoding="utf-8") as file:
            for line in file:
                if not line.strip():
                    continue

                total += 1

                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    malformed += 1
                    continue

                event_id = event.get("event_id") if isinstance(event, dict) else None

                if not event_id:
                    malformed += 1
                    continue

                if event_id in seen_event_ids:
                    duplicates += 1
                else:
                    seen_event_ids.add(event_id)

    return total, malformed, duplicates


def generate_data_quality():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    total_events, malformed_events, duplicate_events = (
        get_source_event_metrics()
    )

    with get_connection() as conn:
        with conn.cursor() as cursor:

            # Lead ingestion totals and duplicate rows merged.
            cursor.execute("""
                SELECT
                    COALESCE(SUM((metrics->>'total_rows')::int), 0),
                    COALESCE(SUM((metrics->>'duplicate_rows_merged')::int), 0)
                FROM app.ingestion_files
                WHERE file_type = 'lead_csv'
                  AND status = 'completed'
            """)
            lead_rows_total, duplicate_lead_rows_merged = cursor.fetchone()

            # Rejected lead rows and rejection reasons.
            cursor.execute("""
                SELECT reason, COUNT(*)
                FROM app.lead_rejections
                GROUP BY reason
                ORDER BY reason
            """)
            rejection_counts = {
                reason: count for reason, count in cursor.fetchall()
            }

            lead_rows_rejected = sum(rejection_counts.values())

            # Optional invalid-field warnings.
            cursor.execute("""
                SELECT COUNT(*) FROM app.field_warnings
            """)
            field_warnings = cursor.fetchone()[0]

            # Events that could not be linked to a lead.
            cursor.execute("""
                SELECT COUNT(*)
                FROM app.interaction_events e
                LEFT JOIN app.event_lead_links l
                    ON l.event_id = e.event_id
                WHERE l.event_id IS NULL
            """)
            orphan_events = cursor.fetchone()[0]

            # Unknown disposition codes in the stored unique events.
            cursor.execute("""
                SELECT COUNT(*)
                FROM app.interaction_events e
                WHERE e.event_type IN (
                    'disposition.set',
                    'disposition.override'
                )
                AND NOT EXISTS (
                    SELECT 1
                    FROM app.dispositions d
                    WHERE d.workflow_id = e.workflow_id
                      AND LOWER(TRIM(d.code)) =
                          LOWER(TRIM(e.payload->>'disposition_code'))
                )
            """)
            unknown_disposition_events = cursor.fetchone()[0]

    quality = {
        "lead_rows_total": lead_rows_total,
        "lead_rows_rejected": lead_rows_rejected,
        "rejections_by_reason": rejection_counts,
        "duplicate_lead_rows_merged": duplicate_lead_rows_merged,
        "field_warnings": field_warnings,
        "events_total": total_events,
        "malformed_events": malformed_events,
        "duplicate_events_dropped": duplicate_events,
        "orphan_events": orphan_events,
        "unknown_disposition_events": unknown_disposition_events,
    }

    output_path = OUTPUT_DIR / "data_quality.json"

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(quality, file, indent=2)

    return output_path


if __name__ == "__main__":
    path = generate_data_quality()
    print(f"Generated: {path}")
