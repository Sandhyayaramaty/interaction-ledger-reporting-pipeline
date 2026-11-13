
import csv

from solution.processing.normalization import (
    NormalizationError,
    build_header_map,
    normalize_field,
)


def validate_lead_row(row: dict, schema: dict):
    """
    Validate and normalize one CSV row.

    Returns:
        (normalized_data, rejection_reason, warnings)

    If rejected:
        normalized_data = None
        rejection_reason = first failure
    """

    fields = schema["fields"]
    header_map = build_header_map(fields)

    # Map original CSV headers to canonical schema field names.
    mapped_row = {}

    for original_header, raw_value in row.items():
        if original_header is None:
            continue

        normalized_header = " ".join(
            original_header.strip().lower().replace("_", " ").split()
        )

        canonical_name = header_map.get(normalized_header)

        if canonical_name is not None:
            # Keep the first non-empty value if aliases are duplicated.
            existing = mapped_row.get(canonical_name)

            if existing is None or str(existing).strip() == "":
                mapped_row[canonical_name] = raw_value

    normalized_data = {}
    warnings = []

    # Validate in schema order.
    for field in fields:
        field_name = field["name"]
        raw_value = mapped_row.get(field_name)

        is_missing = (
            raw_value is None or str(raw_value).strip() == ""
        )

        if is_missing and field.get("required", False):
            return (
                None,
                f"missing_required:{field_name}",
                warnings,
            )

        try:
            normalized_value = normalize_field(field, raw_value)

        except NormalizationError as error:
            if field.get("required", False):
                return None, str(error), warnings

            normalized_value = None
            warnings.append({
                "field_name": field_name,
                "reason": str(error),
            })

        normalized_data[field_name] = normalized_value

    return normalized_data, None, warnings


def read_csv_rows(file_path):
    """
    Read CSV rows using UTF-8 with BOM support.
    """
    with open(
        file_path,
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        for row in reader:
            # Ignore fully blank rows.
            if not any(
                value is not None and str(value).strip()
                for value in row.values()
            ):
                continue

            yield row
