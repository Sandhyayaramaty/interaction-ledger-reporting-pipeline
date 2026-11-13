from solution.processing.lead_metrics import calculate_lead_metrics
from solution.processing.lead_report_data import load_lead_report_data
from solution.processing.workflow_codes import load_workflow_codes


def build_lead_report_rows():
    leads = load_lead_report_data()
    _, success_codes = load_workflow_codes()

    rows = []

    for lead in leads:
        workflow_id = lead["workflow_id"]
        calls = lead["calls"]

        metrics = calculate_lead_metrics(
            calls,
            success_codes[workflow_id],
        )

        rows.append({
            "workflow_id": workflow_id,
            "external_ref": lead["external_ref"],
            "batch_id": lead["batch_id"],
            "phone_encrypted": lead["phone_encrypted"],
            "bucket": lead["bucket"],
            "total_calls": metrics["total_calls"],
            "connected_calls": metrics["connected_calls"],
            "last_call_at": metrics["last_call_at"],
            "current_disposition": metrics["current_disposition"],
            "ever_success": metrics["ever_success"],
        })

    rows.sort(
        key=lambda row: (
            row["workflow_id"],
            row["external_ref"],
        )
    )

    return rows