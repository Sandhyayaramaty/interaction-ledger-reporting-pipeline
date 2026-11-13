
import json
from pathlib import Path


SCHEMA_DIRECTORY = (
    Path(__file__).resolve().parents[2]
    / "assignment-a-data"
    / "schemas"
)


def load_schema(workflow_id: str) -> dict:
    """
    Load the JSON schema for a workflow.

    Example:
        load_schema("motor_renewal")
    """
    schema_path = SCHEMA_DIRECTORY / f"{workflow_id}.json"

    if not schema_path.exists():
        raise FileNotFoundError(
            f"Schema not found for workflow: {workflow_id}"
        )

    with schema_path.open("r", encoding="utf-8") as file:
        schema = json.load(file)

    if schema.get("workflow_id") != workflow_id:
        raise ValueError(
            f"Workflow ID mismatch in schema: {schema_path}"
        )

    return schema


def load_all_schemas() -> dict:
    """Load all workflow schemas."""
    schemas = {}

    for schema_path in sorted(SCHEMA_DIRECTORY.glob("*.json")):
        with schema_path.open("r", encoding="utf-8") as file:
            schema = json.load(file)

        workflow_id = schema["workflow_id"]
        schemas[workflow_id] = schema

    return schemas
