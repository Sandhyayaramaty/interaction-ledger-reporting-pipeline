from solution.db import get_connection


def load_linked_events():
    """
    Load all events that are linked to a lead.

    Returns events grouped later by call_id.
    """

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    e.event_id,
                    e.event_type,
                    e.workflow_id,
                    e.call_id,
                    e.occurred_at,
                    e.payload,
                    l.lead_id
                FROM app.interaction_events e
                JOIN app.event_lead_links el
                    ON el.event_id = e.event_id
                JOIN app.leads l
                    ON l.lead_id = el.lead_id
                ORDER BY
                    e.workflow_id,
                    e.call_id,
                    e.occurred_at,
                    e.event_id
                """
            )

            columns = [column.name for column in cursor.description]

            return [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]