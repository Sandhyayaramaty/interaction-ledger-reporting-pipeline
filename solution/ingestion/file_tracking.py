
import hashlib
import json
from pathlib import Path

from solution.db import get_connection


def calculate_file_hash(file_path: str) -> str:
    return hashlib.sha256(
        Path(file_path).read_bytes()
    ).hexdigest()


def register_completed_file(
    file_path: str,
    workflow_id: str,
    metrics: dict,
):
    path = Path(file_path)
    batch_id = path.stem
    file_hash = calculate_file_hash(file_path)

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
                    status,
                    metrics,
                    completed_at
                )
                VALUES (%s, 'lead_csv', %s, %s, %s,
                        'completed', %s, NOW())
                ON CONFLICT (file_path) DO NOTHING
                RETURNING file_id
                """,
                (
                    str(path),
                    workflow_id,
                    batch_id,
                    file_hash,
                    json.dumps(metrics),
                ),
            )

            result = cursor.fetchone()

    return result[0] if result else None
