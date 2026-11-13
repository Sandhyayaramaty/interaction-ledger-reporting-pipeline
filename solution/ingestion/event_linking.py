
def link_events_to_leads(conn):
    """
    Link events containing a phone hash directly to leads.
    Link phone-less override events through their call_id.
    """

    with conn.cursor() as cursor:

        # Case 1: Events with phone hashes.
        cursor.execute(
            """
            INSERT INTO app.event_lead_links (event_id, lead_id)
            SELECT
                e.event_id,
                l.lead_id
            FROM app.interaction_events e
            JOIN app.leads l
              ON l.workflow_id = e.workflow_id
             AND l.phone_lookup_hash = e.phone_lookup_hash
            WHERE e.phone_lookup_hash IS NOT NULL
            ON CONFLICT (event_id) DO NOTHING
            """
        )

        phone_linked = cursor.rowcount

        # Case 2: Phone-less overrides.
        # Find another event from the same call that is already linked.
        cursor.execute(
            """
            INSERT INTO app.event_lead_links (event_id, lead_id)
            SELECT
                override_event.event_id,
                related.lead_id
            FROM app.interaction_events override_event
            CROSS JOIN LATERAL (
                SELECT linked_event.lead_id
                FROM app.interaction_events related_event
                JOIN app.event_lead_links linked_event
                ON linked_event.event_id = related_event.event_id
                WHERE related_event.workflow_id = override_event.workflow_id
                AND related_event.call_id = override_event.call_id
                AND related_event.event_id <> override_event.event_id
                ORDER BY related_event.occurred_at DESC, related_event.event_id
                LIMIT 1
            ) related
            WHERE override_event.event_type = 'disposition.override'
            AND override_event.phone_lookup_hash IS NULL
            ON CONFLICT (event_id) DO NOTHING;
             """
        )

        override_linked = cursor.rowcount

    return {
        "phone_linked": phone_linked,
        "override_linked": override_linked,
    }
