
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


class NormalizationError(ValueError):
    """Raised when a field contains an invalid value."""


def normalize_header(header: str) -> str:
    """
    Normalize CSV headers:
    - lowercase
    - trim leading/trailing spaces
    - replace consecutive underscores or whitespace with one space
    """
    return re.sub(r"[_\s]+", " ", header.strip().lower())


def build_header_map(fields: list[dict]) -> dict:
    """
    Build a mapping from normalized header names and aliases
    to their canonical schema field names.
    """
    header_map = {}

    for field in fields:
        canonical_name = field["name"]
        possible_names = [canonical_name] + field.get("aliases", [])

        for name in possible_names:
            normalized = normalize_header(name)

            if (
                normalized in header_map
                and header_map[normalized] != canonical_name
            ):
                raise ValueError(
                    f"Ambiguous schema header alias: {name}"
                )

            header_map[normalized] = canonical_name

    return header_map


def normalize_phone(value: str) -> str:
    """
    Convert valid Indian mobile numbers into +91XXXXXXXXXX format.
    """
    digits = re.sub(r"\D", "", str(value))

    if len(digits) == 12 and digits.startswith("91"):
        digits = digits[2:]
    elif len(digits) == 11 and digits.startswith("0"):
        digits = digits[1:]

    if len(digits) != 10 or digits[0] not in "6789":
        raise NormalizationError("invalid_phone")

    return "+91" + digits


def normalize_date(value: str) -> str:
    """
    Supported formats:
    YYYY-MM-DD
    DD/MM/YYYY
    DD-MM-YYYY
    DD-Mon-YYYY

    Returns ISO format: YYYY-MM-DD.
    """
    value = str(value).strip()

    formats = (
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%d-%b-%Y",
    )

    for date_format in formats:
        try:
            parsed = datetime.strptime(value, date_format).date()
            return parsed.isoformat()
        except ValueError:
            continue

    raise NormalizationError("invalid_date")


def normalize_decimal(value: str) -> str:
    """
    Supports optional ₹, Rs, Rs., INR prefixes
    and comma-separated thousands.

    Returns a decimal string with two places.
    """
    value = str(value).strip()

    value = re.sub(
        r"^(?:₹|rs\.?|inr)\s*",
        "",
        value,
        flags=re.IGNORECASE,
    ).strip()

    # Accept normal numbers or correctly grouped thousands.
    valid_number = re.fullmatch(
        r"(?:\d+|\d{1,3}(?:,\d{3})+)(?:\.\d+)?",
        value,
    )

    if not valid_number:
        raise NormalizationError("invalid_decimal")

    try:
        amount = Decimal(value.replace(",", ""))

        if amount < 0:
            raise NormalizationError("invalid_decimal")

        amount = amount.quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

        return format(amount, "f")

    except InvalidOperation:
        raise NormalizationError("invalid_decimal")


def normalize_enum(value: str, allowed_values: list[str]) -> str:
    """
    Compare enum values case-insensitively.
    Store the lowercase value.
    """
    normalized = str(value).strip().lower()
    allowed = {item.lower() for item in allowed_values}

    if normalized not in allowed:
        raise NormalizationError("invalid_enum")

    return normalized


def normalize_field(field: dict, raw_value):
    """
    Normalize a value according to its schema field definition.

    Returns None for missing values.
    Raises NormalizationError for invalid present values.
    """
    if raw_value is None or str(raw_value).strip() == "":
        return None

    field_type = field["type"]

    if field_type == "string":
        return str(raw_value).strip()

    if field_type == "phone":
        return normalize_phone(raw_value)

    if field_type == "date":
        return normalize_date(raw_value)

    if field_type == "decimal":
        return normalize_decimal(raw_value)

    if field_type == "enum":
        return normalize_enum(raw_value, field.get("values", []))

    raise ValueError(f"Unsupported field type: {field_type}")
