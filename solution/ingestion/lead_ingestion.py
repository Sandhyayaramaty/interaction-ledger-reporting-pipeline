
import hashlib
import json
from pathlib import Path

from solution.db import get_connection
from solution.processing.schema_loader import load_schema
from solution.processing.lead_validator import (
    validate_lead_row,
    read_csv_rows,
)
from solution.processing.lead_record import prepare_lead_record
from solution.processing.encryption import hash_phone
from solution.ingestion.leads import upsert_lead


def ingest_lead_file(file_path: str, workflow_id: str):
    file_path = Path(file_path)

    if not file_path.is_file():
        raise FileNotFoundError(file_path)

    batch_id = file_path.stem
    stored_path = str(file_path)

    file_hash = hashlib.sha256(
        file_path.read_bytes()
    ).hexdigest()

    schema = load_schema(workflow_id)

    metrics = {
        "total_rows": 0,
        "accepted_rows": 0,
        "rejected_rows": 0,
        "duplicate_rows_merged": 0,
        "field_warnings": 0,
    }

    rejection_records = []
    warning_records = []

    # One transaction covers tracking and all database changes.
    with get_connection() as conn:

        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO app.ingestion_files (
                    file_path,
                    file_type,
                    workflow_id,
                    batch_id,
                    content_sha256,
                    status
                )
                VALUES (%s, 'lead_csv', %s, %s, %s, 'processing')
                ON CONFLICT (file_path) DO NOTHING
                RETURNING file_id
                """,
                (
                    stored_path,
                    workflow_id,
                    batch_id,
                    file_hash,
                ),
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
                        "Could not retrieve existing ingestion record."
                    )

                existing_hash, existing_status, existing_metrics = existing

                if existing_hash != file_hash:
                    raise ValueError(
                        "This file path was previously ingested "
                        "with different contents. Manual reprocessing "
                        "is required."
                    )

                if existing_status == "completed":
                    result = dict(existing_metrics)
                    result["skipped"] = True
                    return result

                raise RuntimeError(
                    f"File already has ingestion status: {existing_status}"
                )

        # Process nonblank CSV rows in order.
        for row_number, row in enumerate(
            read_csv_rows(file_path), start=1
        ):
            metrics["total_rows"] += 1

            data, rejection, warnings = validate_lead_row(
                row, schema
            )

            if rejection:
                metrics["rejected_rows"] += 1

                rejection_records.append((
                    workflow_id,
                    batch_id,
                    stored_path,
                    row_number,
                    rejection,
                ))
                continue

            metrics["accepted_rows"] += 1
            metrics["field_warnings"] += len(warnings)

            for warning in warnings:
                warning_records.append((
                    workflow_id,
                    batch_id,
                    stored_path,
                    row_number,
                    warning["field_name"],
                    warning["reason"],
                ))

            phone_hash = hash_phone(data["phone"])

            # Count whether this valid row merges with an existing lead.
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT 1
                    FROM app.leads
                    WHERE workflow_id = %s
                    AND phone_lookup_hash = %s
                    """,
                    (workflow_id, phone_hash),
                )
                already_exists = cursor.fetchone() is not None

            record = prepare_lead_record(
                data, schema, batch_id
            )

            upsert_lead(conn, record)

            if already_exists:
                metrics["duplicate_rows_merged"] += 1

        # Save rejections without PII.
        with conn.cursor() as cursor:
            if rejection_records:
                cursor.executemany(
                    """
                    INSERT INTO app.lead_rejections (
                        workflow_id,
                        batch_id,
                        source_file,
                        row_number,
                        reason
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    rejection_records,
                )

            if warning_records:
                cursor.executemany(
                    """
                    INSERT INTO app.field_warnings (
                        workflow_id,
                        batch_id,
                        source_file,
                        row_number,
                        field_name,
                        reason
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    warning_records,
                )

            # Mark the file complete in the same transaction.
            cursor.execute(
                """
                UPDATE app.ingestion_files
                SET status = 'completed',
                    metrics = %s,
                    completed_at = NOW()
                WHERE file_path = %s
                """,
                (
                    json.dumps(metrics),
                    stored_path,
                ),
            )

    return metrics
