
def get_lead_bucket(call_records, terminal_codes):
    """
    Determine the reporting bucket for one lead.
    """

    if not call_records:
        return "yet_to_reach_out"

    # Any terminal effective disposition completes the lead.
    for call in call_records:
        disposition = call.get("effective_disposition")

        if disposition in terminal_codes:
            return "completed"

    # Only classify as telephony failure if every call failed.
    if all(
        call["telephony_failed"]
        for call in call_records
    ):
        return "in_progress_telephony_failed"

    return "in_progress_dialed"
