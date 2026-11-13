
from solution.ingestion.file_tracking import register_completed_file


metrics = {
    "total_rows": 416,
    "accepted_rows": 403,
    "rejected_rows": 13,
    "duplicate_rows_merged": 14,
    "field_warnings": 28,
}

file_id = register_completed_file(
    "data/drop_1/leads/motor_renewal/batch_001.csv",
    "motor_renewal",
    metrics,
)

if file_id is None:
    print("File was already registered.")
else:
    print("Successfully registered existing batch:", file_id)
