# Assignment A: Interaction Ledger & Reporting Pipeline

## 1. Overview

This solution implements a data ingestion, interaction-event processing, and reporting pipeline using Python and PostgreSQL.

It processes lead CSV files and interaction events in JSONL format for two workflows:

- `motor_renewal`
- `policy_feedback`

The pipeline validates and normalizes input data, protects personally identifiable information (PII), merges duplicate leads, stores interaction events, links events to leads, calculates call-level and lead-level metrics, and generates the required reports.

## 2. Technology Stack

- **Language:** Python 3.11
- **Database:** PostgreSQL
- **Database driver:** psycopg
- **PII encryption:** Cryptography (Fernet)
- **Deterministic lookup:** HMAC-SHA256
- **Testing:** unittest
- **Input formats:** CSV and JSONL
- **Output formats:** CSV and JSON

## 3. Architecture

The implementation is organized into the following layers:

1. **Ingestion:** Reads lead CSV files and interaction-event JSONL files.
2. **Normalization and validation:** Standardizes headers, phone numbers, dates, decimals, enums, and timestamps.
3. **Secure storage:** Encrypts sensitive lead fields and stores deterministic phone lookup hashes.
4. **Event linking:** Links stored interaction events to leads using workflow and phone identity, with call-ID-based linking for disposition overrides.
5. **Call processing:** Builds call records from linked events and calculates effective dispositions and call statuses.
6. **Lead processing:** Calculates lead buckets and lead-level metrics.
7. **Reporting:** Generates the five required output files.

### Database design

The PostgreSQL `app` schema contains:

- `leads`: Stores lead identity, encrypted PII, and normalized attributes.
- `interaction_events`: Stores unique interaction events.
- `event_lead_links`: Maintains event-to-lead relationships.
- `lead_rejections`: Records rejected lead rows and reasons.
- `field_warnings`: Records optional-field validation warnings.
- `ingestion_files`: Tracks processed source files and ingestion metrics.
- `dispositions`: Stores workflow-specific disposition definitions.

The schema is exported in `solution/schema.sql`, and the required disposition configuration is included in `solution/seed.sql`.

## 4. Important Implementation Decisions

### Lead ingestion

- Header names are normalized and matched against schema fields and aliases.
- Values are trimmed and validated.
- Indian mobile numbers are normalized to `+91XXXXXXXXXX`.
- Supported date and decimal formats are normalized.
- Required-field failures and invalid phone numbers result in row rejection.
- Invalid optional fields are stored as null and recorded as warnings.
- Duplicate leads are identified using workflow ID and deterministic phone hash.
- Duplicate records update non-null values without replacing the original batch ID.
- Database uniqueness constraints and upsert logic prevent duplicate lead creation.

### PII protection

Sensitive values are encrypted using Fernet before database storage.

A deterministic HMAC-SHA256 hash of the normalized phone number is used for identity matching. This allows duplicate detection and event linking without storing phone numbers in plaintext.

Encryption and HMAC keys are generated locally and stored in `solution/keys.json`. This file is excluded from version control.

**Important:** Keys must be generated once for a fresh environment. Existing keys must not be replaced when encrypted database records need to remain readable.

### Event ingestion and linking

- Each event is identified by its unique `event_id`.
- Duplicate event IDs are ignored.
- Malformed JSON records and records without an event ID are counted and skipped.
- Events without a matching lead remain in the interaction ledger as orphans.
- Event linking can be retried after leads are available.
- Phone-less disposition overrides are linked through related events with the same workflow and call ID.
- Unsupported phone numbers are preserved as unlinked events rather than silently discarded.

### Call and disposition processing

- A call is counted only when a linked `call.initiated` event exists.
- Connected status is derived from `call.connected`.
- Telephony failure is derived from `call.telephony_failed`.
- Call dates are calculated in Indian Standard Time (IST).
- The latest valid disposition override takes precedence over disposition-set events.
- Unknown disposition codes are ignored for effective disposition calculations and counted in data-quality metrics.

### Lead bucketing

Leads are assigned to the following buckets:

1. `yet_to_reach_out`: No valid calls exist.
2. `completed`: At least one call has an effective terminal disposition.
3. `in_progress_telephony_failed`: Every call has a telephony failure.
4. `in_progress_dialed`: All other leads with calls.

### Reporting

The pipeline generates:

| Output | Description |
|---|---|
| `lead_report.csv` | Lead-level call metrics, bucket, masked phone, disposition, and success history |
| `batch_summary.csv` | Lead counts by workflow, batch, and bucket |
| `daily_overview.csv` | Daily call and connectivity metrics |
| `rejections.csv` | Rejected lead rows and reasons without PII |
| `data_quality.json` | Ingestion, rejection, duplicate, orphan, and warning metrics |

Reports are written to the `reports/` directory by default.

## 5. Setup and Execution

### Prerequisites

- Python 3.11 or later
- PostgreSQL
- Assignment input data

Run all commands from the project root.

### Step 1: Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### Step 2: Configure the PostgreSQL password

In PowerShell:

```powershell
$secure = Read-Host "Enter PostgreSQL password" -AsSecureString
$env:PGPASSWORD = [System.Net.NetworkCredential]::new("", $secure).Password
```

The application reads its connection settings from environment variables. Defaults are configured in `solution/config.py`.

### Step 3: Create the database

```powershell
createdb -U postgres -h localhost -p 5432 interaction_ledger
```

If the database already exists, do not create it again.

### Step 4: Create the database schema

```powershell
psql -U postgres -h localhost -p 5432 -d interaction_ledger -f solution/schema.sql
```

### Step 5: Insert disposition configuration

```powershell
psql -U postgres -h localhost -p 5432 -d interaction_ledger -f solution/seed.sql
```

### Step 6: Place the assignment input data

Keep the supplied drop structure under the `data/` directory. The runner automatically discovers lead CSV files and event JSONL files.

Expected structure:

```text
data/
├── drop_1/
│   ├── leads/
│   │   ├── motor_renewal/
│   │   └── policy_feedback/
│   └── events/
└── drop_2/
    ├── leads/
    │   ├── motor_renewal/
    │   └── policy_feedback/
    └── events/
```

Additional drops with the same directory structure can also be discovered automatically.

### Step 7: Run the complete pipeline

```powershell
python -m solution.run
```

The runner checks the database and disposition configuration, generates encryption keys if they do not exist, processes lead and event files, links events to leads, and generates all five reports.

The default input, output, and encryption-key paths can be overridden using `DATA_DIR`, `REPORTS_DIR`, and `ENCRYPTION_KEY_FILE` environment variables.

### Step 8: Run automated tests

```powershell
python -m unittest discover -s solution/tests -v
```

## 6. Verification Results

The implementation was executed against the supplied assignment dataset.

| Metric | Result |
|---|---:|
| Lead rows processed | 2,057 |
| Accepted lead rows | 1,949 |
| Rejected lead rows | 108 |
| Unique leads stored | 1,892 |
| Duplicate lead rows merged | 57 |
| Optional-field warnings | 122 |
| Non-empty event records | 8,745 |
| Unique events stored | 8,500 |
| Malformed events | 8 |
| Duplicate event IDs dropped | 237 |
| Linked events | 8,038 |
| Orphan events | 462 |
| Unknown disposition events | 19 |
| Calls built from linked events | 2,536 |
| Connected calls | 1,467 |

### Lead bucket distribution

| Bucket | Leads |
|---|---:|
| `completed` | 816 |
| `in_progress_dialed` | 526 |
| `in_progress_telephony_failed` | 38 |
| `yet_to_reach_out` | 512 |
| **Total** | **1,892** |

### Automated tests

All 52 automated tests passed:

```text
Ran 52 tests
OK
```

The tests cover normalization, validation, phone and date handling, duplicate insertion, event validation, disposition selection, call processing, lead bucketing, reporting data, sorting, and phone masking.

### Additional seed and idempotency validation

The pipeline was also executed against a separately generated dataset using seed `12345`, with a separate PostgreSQL database and encryption key.

The pipeline completed successfully and generated all five reports.

After rerunning the pipeline with the same input, database counts remained unchanged:

| Database table | Records |
|---|---:|
| Leads | 1,914 |
| Interaction events | 8,763 |
| Event-lead links | 8,312 |

This verified that repeated execution does not create duplicate database records for the same input.

## 7. Limitations and Future Improvements

- Performance benchmarking against larger datasets was not completed.
- Concurrent ingestion and high-volume stress testing were not performed.
- Production deployment, monitoring, and scheduled ingestion were outside the implemented scope.
- A future version could add structured logging, retry policies, monitoring dashboards, and automated report scheduling.
- Additional integration tests could validate the complete pipeline against independently recreated databases.

## 8. Conclusion

The solution implements the core lead-ingestion, secure event-ledger, event-linking, call-processing, and reporting requirements for Assignment A. It was validated against the supplied dataset and an independently generated seed, with all 52 automated tests passing.