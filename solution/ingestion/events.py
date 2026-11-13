
from psycopg.types.json import Jsonb


def insert_event(conn, event: dict, source_file: str, line_number: int):
    query = """
        INSERT INTO app.interaction_events (
            event_id,
            event_type,
            workflow_id,
            call_id,
            occurred_at,
            phone_lookup_hash,
            payload,
            source_file,
            line_number
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (event_id) DO NOTHING
        RETURNING event_id;
    """

    with conn.cursor() as cursor:
        cursor.execute(
            query,
            (
                event["event_id"],
                event["event_type"],
                event["workflow_id"],
                event["call_id"],
                event["occurred_at"],
                event["phone_lookup_hash"],
                Jsonb(event["payload"]),
                source_file,
                line_number,
            ),
        )

        result = cursor.fetchone()

    return result is not None
