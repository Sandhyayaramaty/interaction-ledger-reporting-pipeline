
from pathlib import Path
from solution.paths import DATA_DIR

from solution.db import get_connection
from solution.processing.encryption import KEY_FILE, generate_keys
from solution.ingestion.lead_ingestion import ingest_lead_file
from solution.ingestion.event_ingestion import ingest_event_file
from solution.ingestion.event_linking import link_events_to_leads

from solution.reporting.lead_report import generate_lead_report
from solution.reporting.batch_summary import generate_batch_summary
from solution.reporting.daily_overview import generate_daily_overview
from solution.reporting.rejections import generate_rejections
from solution.reporting.data_quality import generate_data_quality


DATA_DIRECTORY = DATA_DIR


def drop_sort_key(path):
    """Sort drop_1, drop_2, drop_10 in numeric order."""
    drop_name = path.parts[1]
    drop_number = int(drop_name.split("_")[1])
    return drop_number


def discover_lead_files():
    """Find every CSV batch across all drops and workflows."""
    files = list(
        DATA_DIRECTORY.glob("drop_*/leads/*/*.csv")
    )

    return sorted(
        files,
        key=lambda path: (
            drop_sort_key(path),
            path.parent.name,
            path.name,
        ),
    )


def discover_event_files():
    """Find every JSONL event file across all drops."""
    files = list(
        DATA_DIRECTORY.glob("drop_*/events/*.jsonl")
    )

    return sorted(
        files,
        key=lambda path: (
            drop_sort_key(path),
            path.name,
        ),
    )


def main():
    print("=" * 60)
    print("INTERACTION LEDGER - DATA PIPELINE")
    print("=" * 60)

    check_database()

    if not DATA_DIRECTORY.exists():
        raise FileNotFoundError(
            "The data directory was not found."
        )

    # Step 1: Generate encryption keys if they do not exist.
    print("\n[1/6] Checking encryption keys...")

    if not KEY_FILE.exists():
        generate_keys()
        print("Encryption keys generated.")
    else:
        print("Existing encryption keys found.")

    # Step 2: Discover and ingest all lead files.
    lead_files = discover_lead_files()

    if not lead_files:
        raise FileNotFoundError(
            "No lead CSV files found."
        )

    print(f"\n[2/6] Ingesting {len(lead_files)} lead files...")

    for file_path in lead_files:
        workflow_id = file_path.parent.name

        print(f"\nProcessing: {file_path}")

        metrics = ingest_lead_file(
            str(file_path),
            workflow_id,
        )

        print("Result:", metrics)

    # Step 3: Discover and ingest all event files.
    event_files = discover_event_files()

    if not event_files:
        raise FileNotFoundError(
            "No event JSONL files found."
        )

    print(f"\n[3/6] Ingesting {len(event_files)} event files...")

    for file_path in event_files:
        print(f"\nProcessing: {file_path}")

        metrics = ingest_event_file(str(file_path))

        print("Result:", metrics)

    # Step 4: Link events to leads.
    print("\n[4/6] Linking events to leads...")

    with get_connection() as conn:
        linking_metrics = link_events_to_leads(conn)

        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*)
                FROM app.interaction_events e
                LEFT JOIN app.event_lead_links l
                    ON l.event_id = e.event_id
                WHERE l.event_id IS NULL
            """)

            orphan_count = cursor.fetchone()[0]

    print("Linking result:", linking_metrics)
    print("Events still unlinked:", orphan_count)

    # Step 5: Generate all reports.
    print("\n[5/6] Generating reports...")

    report_generators = [
        ("Lead report", generate_lead_report),
        ("Batch summary", generate_batch_summary),
        ("Daily overview", generate_daily_overview),
        ("Rejections", generate_rejections),
        ("Data quality", generate_data_quality),
    ]

    for report_name, generator in report_generators:
        print(f"\nGenerating {report_name}...")
        generator()

    # Step 6: Finish.
    print("\n[6/6] Pipeline completed.")

    print("\nGenerated reports are available in:")
    print("reports/")

    print("\nAll processing steps completed successfully.")


def check_database():
    """Verify that the database schema and reference data are ready."""

    required_tables = [
        "leads",
        "interaction_events",
        "event_lead_links",
        "lead_rejections",
        "field_warnings",
        "ingestion_files",
        "dispositions",
    ]

    print("\nChecking PostgreSQL database...")

    with get_connection() as conn:
        with conn.cursor() as cursor:

            missing_tables = []

            for table in required_tables:
                cursor.execute(
                    "SELECT to_regclass(%s)",
                    (f"app.{table}",),
                )

                if cursor.fetchone()[0] is None:
                    missing_tables.append(table)

            if missing_tables:
                raise RuntimeError(
                    "Database schema is incomplete. "
                    "Missing tables: "
                    + ", ".join(missing_tables)
                    + ". Please execute solution/schema.sql."
                )

            cursor.execute(
                "SELECT COUNT(*) FROM app.dispositions"
            )

            disposition_count = cursor.fetchone()[0]

            if disposition_count != 14:
                raise RuntimeError(
                    f"Expected 14 disposition records, "
                    f"but found {disposition_count}. "
                    "Please execute solution/seed.sql."
                )

    print("Database connection: OK")
    print("Required tables: OK")
    print("Disposition configuration: OK")



if __name__ == "__main__":
    main()
