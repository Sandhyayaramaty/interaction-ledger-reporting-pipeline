
def get_effective_disposition(events, valid_codes):
    """
    Determine the effective disposition for one call.

    events: list of event dictionaries
    valid_codes: set of valid disposition codes
    """

    valid_overrides = []
    valid_sets = []

    for event in events:
        if event["event_type"] not in (
            "disposition.set",
            "disposition.override",
        ):
            continue

        code = event.get("payload", {}).get("disposition_code")

        if not isinstance(code, str):
            continue

        code = code.strip().lower()

        if code not in valid_codes:
            continue

        normalized_event = {
            "code": code,
            "occurred_at": event["occurred_at"],
        }

        if event["event_type"] == "disposition.override":
            valid_overrides.append(normalized_event)
        else:
            valid_sets.append(normalized_event)

    candidates = valid_overrides if valid_overrides else valid_sets

    if not candidates:
        return None

    latest = max(
        candidates,
        key=lambda item: item["occurred_at"],
    )

    return latest["code"]