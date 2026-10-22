# Typed Data Processing Toolkit

A small, production-minded Python project for validating and normalizing moderately sized CSV or JSON datasets. It demonstrates type hints, dataclasses, algorithms, standard-library collections, a command-line interface, testing, and performance reasoning.

## What it does

The pipeline follows a predictable sequence:

1. **Read** CSV rows or a JSON array of objects.
2. **Normalize** field names and text (trim whitespace, collapse spaces, lowercase email, title-case country).
3. **Validate** required fields, email shape, and age as an integer in the inclusive range 0–120.
4. **Detect duplicates** by `record_id`. The first valid occurrence is retained; later occurrences are written to the invalid output.
5. **Write outputs** and a machine-readable summary report.

The input schema is:

| Field | Type | Rules |
|---|---|---|
| `record_id` | string | Required; unique among accepted records |
| `name` | string | Required; whitespace normalized |
| `email` | string | Required; basic `name@domain.tld` shape; lowercased |
| `age` | integer | Required; 0–120 inclusive |
| `country` | string | Required; whitespace normalized and title-cased |

The email check is intentionally pragmatic, not a complete implementation of every email-address standard. It does not verify that a mailbox exists.

## Requirements

- Python 3.10+
- No runtime third-party dependencies
- Optional development tools: `pytest` and `ruff`

## Setup

From the project root:

```bash
python -m venv .venv
```

Activate the environment:

- Windows PowerShell: `.venv\Scripts\Activate.ps1`
- macOS/Linux: `source .venv/bin/activate`

Install the project and developer tools:

```bash
python -m pip install -e ".[dev]"
```

If you only want to run it without installing, set `PYTHONPATH=src` (PowerShell: `$env:PYTHONPATH="src"`).

## CLI usage

```bash
data-toolkit data/people.csv --output-dir output
data-toolkit data/people.json --output-dir output-json
data-toolkit --help
```

Alternative without installation:

```bash
python -m data_toolkit.cli data/people.csv --output-dir output
```

### Outputs

- `clean.csv`: normalized records that passed all checks.
- `invalid.json`: each rejected row's 1-based input row number, original source data, and one or more error codes.
- `report.json`: input format, total/clean/invalid counts, per-error counts, duplicate count, and elapsed processing time.

The report's `total_records` is the number of input items processed, not the number of physical lines in the source file. CSV `row_number` starts at 1 for the first data record (the header is not counted); JSON item numbering likewise starts at 1.

Example report:

```json
{
  "input_path": "data/people.csv",
  "input_format": "csv",
  "total_records": 1000,
  "clean_records": 972,
  "invalid_records": 28,
  "error_counts": {
    "invalid_email:expected_name_at_domain": 12,
    "invalid_age:must_be_between_0_and_120": 5,
    "duplicate_record_id": 11
  },
  "duplicate_ids": 11,
  "elapsed_seconds": 0.034
}
```

Numbers above are illustrative; elapsed time depends on hardware and data.

## Example data

The `data/people.csv` file contains 1,000 sample rows with intentional validation failures and duplicate IDs. The `data/people.json` file contains a smaller equivalent example, including a non-object item to demonstrate invalid JSON-array records.

Run the CSV sample:

```bash
data-toolkit data/people.csv --output-dir output
```

Inspect `output/report.json` first, then review `output/invalid.json` for the exact records and actionable error codes.

## Tests and code quality

```bash
pytest
ruff check src tests
```

Tests cover normalization, typed output, invalid age/email, missing fields, duplicate handling, generated output files, and malformed JSON item shapes.

## Design decisions and data structures

- **Dataclasses (`CleanRecord`, `InvalidRecord`, `ProcessingReport`)** give the pipeline explicit record shapes and keep output serialization predictable. `frozen=True` prevents accidental mutation after construction; `slots=True` reduces per-instance overhead.
- **`set[str]` for duplicate IDs** provides expected O(1) membership checks and avoids a nested-loop duplicate scan, which would be O(n²).
- **`Counter[str]` for validation errors** counts error types clearly without manual dictionary bookkeeping.
- **Lists** preserve input order for clean and invalid output. That is useful for debugging and makes runs deterministic.
- **Generators / iterators** stream CSV rows instead of first loading the entire file. JSON parsing uses the standard library's `json.load`, which materializes the JSON document in memory.
- **Type hints** clarify interfaces and make future static checking easier. Runtime validation is still necessary because CSV and JSON values are untrusted external data.
- **Pipeline stages are separated** into I/O, models, validation/transformation, and CLI modules. That makes the core logic unit-testable without invoking a shell.

## Complexity and performance notes

Let `n` be the number of input records and `k` the average number of fields per record.

- Reading and validating each row is O(k); overall normalization/validation is O(n·k).
- Duplicate detection is expected O(n) total with a hash set, rather than O(n²) pairwise comparisons.
- Writing outputs is O(n) in the number of output records.
- The CSV reader is lazy, but the pipeline currently retains clean and invalid records in lists so it can produce outputs and summary counts. Memory use is therefore O(n·k), plus the set of IDs. This is appropriate for moderately sized files (for example, tens of thousands to a few hundred thousand rows, depending on available RAM and row width), not arbitrarily large datasets.
- JSON input is loaded as a complete document by the standard library, so its peak memory usage is higher than CSV streaming.
- `elapsed_seconds` includes input parsing, processing, and output writes. It is an observation from one run, not a benchmark guarantee.

## Error-handling policy

Known input problems (unsupported extension, missing file, malformed JSON) produce a concise error on stderr and exit code `2`. Invalid *records* do not abort the run; they are written to `invalid.json` so a user can repair them. Error codes are intended to be machine-readable.

## Project tree

```text
typed_data_toolkit/
├── data/
│   ├── people.csv
│   └── people.json
├── src/data_toolkit/
│   ├── __init__.py
│   ├── cli.py
│   ├── io.py
│   ├── models.py
│   └── pipeline.py
├── tests/
│   └── test_pipeline.py
├── pyproject.toml
└── README.md
```