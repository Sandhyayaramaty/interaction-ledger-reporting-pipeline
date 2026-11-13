
from solution.processing.event_normalization import IST


def calculate_lead_metrics(calls, success_codes):
    """
    Calculate reporting metrics for one lead.
    """

    if not calls:
        return {
            "total_calls": 0,
            "connected_calls": 0,
            "last_call_at": None,
            "current_disposition": None,
            "ever_success": False,
        }

    ordered_calls = sorted(
        calls,
        key=lambda call: call["initiated_at"],
    )

    # Most recent call with a valid effective disposition.
    calls_with_disposition = [
        call for call in ordered_calls
        if call["effective_disposition"] is not None
    ]

    current_disposition = (
        calls_with_disposition[-1]["effective_disposition"]
        if calls_with_disposition
        else None
    )

    ever_success = any(
        call["effective_disposition"] in success_codes
        for call in ordered_calls
    )

    latest_call = ordered_calls[-1]

    return {
        "total_calls": len(ordered_calls),
        "connected_calls": sum(
            1 for call in ordered_calls
            if call["connected"]
        ),
        "last_call_at": latest_call["initiated_at"].astimezone(IST),
        "current_disposition": current_disposition,
        "ever_success": ever_success,
    }
