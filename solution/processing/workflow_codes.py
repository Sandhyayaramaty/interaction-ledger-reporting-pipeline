
from collections import defaultdict

from solution.db import get_connection


def load_workflow_codes():
    terminal_codes = defaultdict(set)
    success_codes = defaultdict(set)

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT workflow_id, code, is_terminal, is_success
                FROM app.dispositions
                """
            )

            for workflow_id, code, is_terminal, is_success in cursor.fetchall():
                if is_terminal:
                    terminal_codes[workflow_id].add(code)

                if is_success:
                    success_codes[workflow_id].add(code)

    return terminal_codes, success_codes
