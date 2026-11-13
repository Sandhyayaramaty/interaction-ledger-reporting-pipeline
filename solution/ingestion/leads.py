
from psycopg.types.json import Jsonb


def upsert_lead(conn, record: dict) -> int:
    """
    Insert a new lead or merge it with an existing lead.

    Duplicate identity:
        workflow_id + phone_lookup_hash

    The original batch_id is preserved.
    Existing attributes are updated only with new non-null values.
    """

    query = """
        INSERT INTO app.leads (
            workflow_id,
            batch_id,
            external_ref,
            phone_lookup_hash,
            phone_encrypted,
            customer_name_encrypted,
            attributes
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)

        ON CONFLICT (workflow_id, phone_lookup_hash)
        DO UPDATE SET
            external_ref = EXCLUDED.external_ref,
            customer_name_encrypted = EXCLUDED.customer_name_encrypted,
            attributes = app.leads.attributes || EXCLUDED.attributes,
            updated_at = NOW()

        RETURNING lead_id;
    """

    with conn.cursor() as cursor:
        cursor.execute(
            query,
            (
                record["workflow_id"],
                record["batch_id"],
                record["external_ref"],
                record["phone_lookup_hash"],
                record["phone_encrypted"],
                record["customer_name_encrypted"],
                Jsonb(record["attributes"]),
            ),
        )

        result = cursor.fetchone()

    return result[0]
