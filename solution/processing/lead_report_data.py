
from collections import defaultdict

from solution.db import get_connection
from solution.processing.call_builder import build_all_call_records
from solution.processing.lead_bucketing import get_lead_bucket


def load_lead_report_data():
    calls = build_all_call_records()

    calls_by_lead = defaultdict(list)

    for call in calls:
        calls_by_lead[
            (call["workflow_id"], call["lead_id"])
        ].append(call)

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT workflow_id, code
                FROM app.dispositions
                WHERE is_terminal = TRUE
                """
            )

            terminal_codes = defaultdict(set)

            for workflow_id, code in cursor.fetchall():
                terminal_codes[workflow_id].add(code)

            cursor.execute(
                """
                SELECT
                    lead_id,
                    workflow_id,
                    batch_id,
                    external_ref,
                    phone_encrypted
                FROM app.leads
                ORDER BY workflow_id, external_ref
                """
            )

            leads = cursor.fetchall()

    results = []

    for (
        lead_id,
        workflow_id,
        batch_id,
        external_ref,
        phone_encrypted,
    ) in leads:

        lead_calls = calls_by_lead.get(
            (workflow_id, lead_id),
            [],
        )

        bucket = get_lead_bucket(
            lead_calls,
            terminal_codes[workflow_id],
        )

        results.append({
            "lead_id": lead_id,
            "workflow_id": workflow_id,
            "batch_id": batch_id,
            "external_ref": external_ref,
            "phone_encrypted": phone_encrypted,
            "bucket": bucket,
            "calls": lead_calls,
        })

    return results
