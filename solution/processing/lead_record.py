
from solution.processing.encryption import encrypt_value, hash_phone


def prepare_lead_record(
    normalized_data: dict,
    schema: dict,
    batch_id: str,
) -> dict:
    """
    Separate PII, reference fields and ordinary attributes
    before storing a lead in PostgreSQL.
    """

    fields = schema["fields"]

    pii_fields = {
        field["name"]
        for field in fields
        if field.get("pii", False)
    }

    reference_fields = [
        field["name"]
        for field in fields
        if field.get("reference", False)
    ]

    # Both workflow schemas have exactly one reference field.
    if len(reference_fields) != 1:
        raise ValueError(
            "Expected exactly one reference field in workflow schema."
        )

    external_ref_field = reference_fields[0]

    customer_name = normalized_data["customer_name"]
    phone = normalized_data["phone"]

    # Never put PII or the external reference in JSONB attributes.
    excluded_fields = pii_fields | {external_ref_field}

    attributes = {
        key: value
        for key, value in normalized_data.items()
        if key not in excluded_fields and value is not None
    }

    return {
        "workflow_id": schema["workflow_id"],
        "batch_id": batch_id,
        "external_ref": normalized_data[external_ref_field],
        "phone_lookup_hash": hash_phone(phone),
        "phone_encrypted": encrypt_value(phone),
        "customer_name_encrypted": encrypt_value(customer_name),
        "attributes": attributes,
    }
