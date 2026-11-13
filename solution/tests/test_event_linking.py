
from solution.ingestion.event_ingestion import ingest_event_file
from solution.ingestion.event_linking import link_events_to_leads
from solution.db import get_connection


FILES = [
    "data/drop_1/events/events_0001.jsonl",
    "data/drop_2/events/events_1001.jsonl",
]


def main():
    for file_path in FILES:
        print(f"\nProcessing: {file_path}")
        metrics = ingest_event_file(file_path)
        print("Result:", metrics)

    print("\nLinking events to leads...")

    with get_connection() as conn:
        linking_metrics = link_events_to_leads(conn)

        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM app.interaction_events e
                LEFT JOIN app.event_lead_links l
                  ON l.event_id = e.event_id
                WHERE l.event_id IS NULL
                """
            )
            orphan_count = cursor.fetchone()[0]

    print("Linking result:", linking_metrics)
    print("Events still unlinked:", orphan_count)


if __name__ == "__main__":
    main()
