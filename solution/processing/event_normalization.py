
from datetime import datetime
from zoneinfo import ZoneInfo


IST = ZoneInfo("Asia/Kolkata")


def normalize_event_timestamp(value: str) -> datetime:
    """
    Convert an event timestamp to timezone-aware IST.

    Naive timestamps are assumed to already represent IST.
    Timestamps with timezone information are converted to IST.
    """
    if not isinstance(value, str) or not value.strip():
        raise ValueError("missing_or_invalid_timestamp")

    try:
        timestamp = datetime.fromisoformat(
            value.strip().replace("Z", "+00:00")
        )
    except ValueError:
        raise ValueError("invalid_timestamp")

    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=IST)
    else:
        timestamp = timestamp.astimezone(IST)

    return timestamp
