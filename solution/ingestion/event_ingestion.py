
import hashlib
import json
from pathlib import Path

from solution.db import get_connection
from solution.processing.event_validator import validate_event
from solution.ingestion.events import insert_event


def ingest_event_file(file_path: str):
    file_path = Path(file_path)

    if not file_path.is_file():
        raise FileNotFoundError(file_path)

    stored_path = str(file_path)

    file_hash = hashlib.sha256(
        file_path.read_bytes()
    ).hexdigest()

    metrics = {
        "events_total": 0,
        "malformed_events": 0,
        "duplicate_events_dropped": 0,
        "orphan_events": 0,
        "unknown_disposition_events": 0,
    }

    with get_connection() as conn:

        # Register the file and prevent accidental reprocessing.
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO app.ingestion_files (
                    file_path,
                    file_type,
                    content_sha256,
                    status
                )
                VALUES (%s, 'event_jsonl', %s, 'processing')
                ON CONFLICT (file_path) DO NOTHING
                RETURNING file_id
                """,
                (stored_path, file_hash),
            )

            inserted = cursor.fetchone()

            if inserted is None:
                cursor.execute(
                    """
                    SELECT content_sha256, status, metrics
                    FROM app.ingestion_files
                    WHERE file_path = %s
                    FOR UPDATE
                    """,
                    (stored_path,),
                )

                existing = cursor.fetchone()

                if existing is None:
                    raise RuntimeError(
                        "Could not retrieve ingestion record."
                    )

                existing_hash, status, existing_metrics = existing

                if existing_hash != file_hash:
                    raise ValueError(
                        "File contents changed after previous ingestion."
                    )

                if status == "completed":
                    print(
                        f"Reprocessing {stored_path} to recover "
                        "events rejected by the earlier validator."
                    )
                elif status != "processing":
                    raise RuntimeError(
                        f"File ingestion status is {status}"
                    )

        with file_path.open("r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):

                if not line.strip():
                    continue

                metrics["events_total"] += 1

                try:
                    raw_event = json.loads(line)
                except json.JSONDecodeError:
                    metrics["malformed_events"] += 1
                    continue

                if (
                    not isinstance(raw_event, dict)
                    or not raw_event.get("event_id")
                ):
                    metrics["malformed_events"] += 1
                    continue

                event, error = validate_event(raw_event)

                if error:
                    metrics["malformed_events"] += 1
                    continue

                inserted = insert_event(
                    conn,
                    event,
                    stored_path,
                    line_number,
                )

                if not inserted:
                    metrics["duplicate_events_dropped"] += 1
                    continue

                if (
                    event["event_type"]
                    in ("disposition.set", "disposition.override")
                ):
                    code = event["payload"].get("disposition_code")

                    if isinstance(code, str):
                        code = code.strip().lower()
                    if code is not None:
                        with conn.cursor() as cursor:
                            cursor.execute(
                                """
                                SELECT 1
                                FROM app.dispositions
                                WHERE workflow_id = %s
                                  AND code = %s
                                """,
                                (event["workflow_id"], code),
                            )

                            if cursor.fetchone() is None:
                                metrics["unknown_disposition_events"] += 1

        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE app.ingestion_files
                SET status = 'completed',
                    metrics = %s,
                    completed_at = NOW()
                WHERE file_path = %s
                """,
                (json.dumps(metrics), stored_path),
            )

    return metrics
