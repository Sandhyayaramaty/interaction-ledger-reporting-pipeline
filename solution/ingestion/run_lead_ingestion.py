
from pathlib import Path

from solution.ingestion.lead_ingestion import ingest_lead_file


DATA_DIRECTORY = Path("data")

FILES = [
    (
        DATA_DIRECTORY / "drop_1/leads/motor_renewal/batch_001.csv",
        "motor_renewal",
    ),
    (
        DATA_DIRECTORY / "drop_1/leads/motor_renewal/batch_002.csv",
        "motor_renewal",
    ),
    (
        DATA_DIRECTORY / "drop_1/leads/policy_feedback/batch_001.csv",
        "policy_feedback",
    ),
    (
        DATA_DIRECTORY / "drop_1/leads/policy_feedback/batch_002.csv",
        "policy_feedback",
    ),
    (
        DATA_DIRECTORY / "drop_2/leads/motor_renewal/batch_003.csv",
        "motor_renewal",
    ),
    (
        DATA_DIRECTORY / "drop_2/leads/policy_feedback/batch_003.csv",
        "policy_feedback",
    ),
]


def main():
    for file_path, workflow_id in FILES:
        print(f"\nProcessing: {file_path}")
        metrics = ingest_lead_file(str(file_path), workflow_id)
        print("Result:", metrics)


if __name__ == "__main__":
    main()
