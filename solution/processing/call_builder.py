from collections import defaultdict

from solution.processing.call_loader import load_linked_events
from solution.processing.call_processing import build_call_record


def load_valid_disposition_codes(conn, workflow_id):
    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT code
            FROM app.dispositions
            WHERE workflow_id = %s
            """,
            (workflow_id,),
        )

        return {
            row[0].strip().lower()
            for row in cursor.fetchall()
        }


def build_all_call_records():
    from solution.db import get_connection

    events = load_linked_events()

    grouped = defaultdict(list)

    for event in events:
        grouped[
            (event["workflow_id"], event["call_id"], event["lead_id"])
        ].append(event)

    call_records = []

    with get_connection() as conn:
        valid_codes_by_workflow = {}

        for workflow_id, _, _ in grouped:
            if workflow_id not in valid_codes_by_workflow:
                valid_codes_by_workflow[workflow_id] = (
                    load_valid_disposition_codes(
                        conn,
                        workflow_id,
                    )
                )

        for (
            workflow_id,
            call_id,
            lead_id,
        ), call_events in grouped.items():

            record = build_call_record(
                call_events,
                valid_codes_by_workflow[workflow_id],
            )

            if record is not None:
                call_records.append(record)

    return call_records