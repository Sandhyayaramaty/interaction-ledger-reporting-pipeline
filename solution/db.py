
import psycopg

from solution.config import DB_CONFIG, validate_config


def get_connection():
    """
    Open a connection to the interaction_ledger database.
    The session uses the app schema by default.
    """
    validate_config()
    return psycopg.connect(**DB_CONFIG)


def test_connection():
    """
    Check that Python can connect to PostgreSQL.
    """
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT current_database(), current_schema();"
            )
            return cursor.fetchone()
