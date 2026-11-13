
import os


DB_CONFIG = {
    "host": os.getenv("PGHOST", "localhost"),
    "port": int(os.getenv("PGPORT", "5432")),
    "dbname": os.getenv("PGDATABASE", "interaction_ledger"),
    "user": os.getenv("PGUSER", "postgres"),
    "password": os.getenv("PGPASSWORD"),
    "options": "-c search_path=app",
}


def validate_config():
    if not DB_CONFIG["password"]:
        raise RuntimeError(
            "PostgreSQL password is missing. "
            "Set the PGPASSWORD environment variable."
        )
