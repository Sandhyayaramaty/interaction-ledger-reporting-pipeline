
from solution.processing.normalization import (
    NormalizationError,
    normalize_phone,
)
from solution.processing.event_normalization import (
    normalize_event_timestamp,
)


VALID_EVENT_TYPES = {
    "call.initiated",
    "call.telephony_failed",
    "call.connected",
    "call.ended",
    "disposition.set",
    "disposition.override",
}


def validate_event(event: dict):
    if not isinstance(event, dict):
        return None, "invalid_event"

    required_fields = [
        "event_id",
        "event_type",
        "workflow_id",
        "call_id",
        "occurred_at",
    ]

    for field in required_fields:
        value = event.get(field)

        if value is None or str(value).strip() == "":
            return None, f"missing_required:{field}"

    if event["event_type"] not in VALID_EVENT_TYPES:
        return None, "unknown_event_type"

    payload = event.get("payload", {})

    if not isinstance(payload, dict):
        return None, "invalid_payload"

    try:
        occurred_at = normalize_event_timestamp(
            event["occurred_at"]
        )
    except ValueError as error:
        return None, str(error)

    phone_hash = None
    raw_phone = event.get("phone")

    if raw_phone is not None and str(raw_phone).strip():
        try:
            normalized_phone = normalize_phone(raw_phone)
            from solution.processing.encryption import hash_phone
            phone_hash = hash_phone(normalized_phone)
        except NormalizationError:
            phone_hash = None


    return {
        "event_id": str(event["event_id"]).strip(),
        "event_type": event["event_type"],
        "workflow_id": event["workflow_id"],
        "call_id": str(event["call_id"]).strip(),
        "occurred_at": occurred_at,
        "phone_lookup_hash": phone_hash,
        "payload": payload,
    }, None
