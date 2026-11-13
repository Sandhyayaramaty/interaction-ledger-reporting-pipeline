from solution.processing.dispositions import get_effective_disposition
from solution.processing.event_normalization import IST


def build_call_record(events, valid_codes):
    """
    Build a summary for one call.

    Only calls containing call.initiated are considered real calls
    for reporting purposes.
    """

    initiated_events = [
        event
        for event in events
        if event["event_type"] == "call.initiated"
    ]

    if not initiated_events:
        return None

    # There should normally be one initiated event.
    # Use the earliest one if duplicates exist in the call.
    initiated = min(
        initiated_events,
        key=lambda event: event["occurred_at"],
    )

    connected = any(
        event["event_type"] == "call.connected"
        for event in events
    )

    telephony_failed = any(
        event["event_type"] == "call.telephony_failed"
        for event in events
    )

    effective_disposition = get_effective_disposition(
        events,
        valid_codes,
    )

    return {
        "call_id": initiated["call_id"],
        "lead_id": initiated.get("lead_id"),
        "workflow_id": initiated["workflow_id"],
        "initiated_at": initiated["occurred_at"],
        "call_date": initiated["occurred_at"].astimezone(IST).date(),
        "connected": connected,
        "telephony_failed": telephony_failed,
        "effective_disposition": effective_disposition,
    }