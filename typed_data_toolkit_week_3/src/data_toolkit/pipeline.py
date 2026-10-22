"""Normalization, validation, deduplication, and reporting."""
from __future__ import annotations

import re
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

from data_toolkit.io import read_records, write_csv, write_json
from data_toolkit.models import CleanRecord, InvalidRecord, ProcessingReport

REQUIRED_FIELDS = ("record_id", "name", "email", "age", "country")
CLEAN_FIELDS = list(REQUIRED_FIELDS)
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _text(value: Any) -> str:
    """Convert a value to trimmed text, treating None as blank."""
    return "" if value is None else str(value).strip()


def normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    """Normalize known text fields without mutating the caller's row."""
    normalized = {str(key).strip().lower(): value for key, value in row.items()}
    for field in REQUIRED_FIELDS:
        if field in normalized:
            normalized[field] = _text(normalized[field])
    normalized["record_id"] = _text(normalized.get("record_id", ""))
    normalized["name"] = " ".join(_text(normalized.get("name", "")).split())
    normalized["email"] = _text(normalized.get("email", "")).lower()
    normalized["country"] = " ".join(_text(normalized.get("country", "")).split()).title()
    return normalized


def validate_row(row: dict[str, Any]) -> tuple[CleanRecord | None, list[str]]:
    """Return a canonical record or a list of actionable validation errors."""
    if "__input_error__" in row:
        return None, [_text(row["__input_error__"])]

    normalized = normalize_row(row)
    errors: list[str] = []

    for field in REQUIRED_FIELDS:
        if not normalized.get(field):
            errors.append(f"missing_required_field:{field}")

    age_value = normalized.get("age", "")
    age: int | None = None
    if age_value != "":
        try:
            # Reject values such as "24.5" rather than silently rounding them.
            age = int(str(age_value))
            if str(age) != str(age_value).strip() and not isinstance(age_value, int):
                raise ValueError
        except (TypeError, ValueError):
            errors.append("invalid_age:must_be_an_integer")
        else:
            if not 0 <= age <= 120:
                errors.append("invalid_age:must_be_between_0_and_120")

    email = str(normalized.get("email", ""))
    if email and not EMAIL_RE.fullmatch(email):
        errors.append("invalid_email:expected_name_at_domain")

    if errors:
        return None, errors

    assert age is not None  # age is guaranteed when there are no validation errors.
    return CleanRecord(
        record_id=str(normalized["record_id"]),
        name=str(normalized["name"]),
        email=email,
        age=age,
        country=str(normalized["country"]),
    ), []


def process_records(rows: Iterable[dict[str, Any]]) -> tuple[list[CleanRecord], list[InvalidRecord], Counter[str], int]:
    """Process input rows in order and flag duplicate IDs after the first occurrence.

    Duplicate detection uses a set for expected O(1) membership checks. The first
    valid occurrence is retained; later rows with that ID are invalidated.
    """
    clean: list[CleanRecord] = []
    invalid: list[InvalidRecord] = []
    error_counts: Counter[str] = Counter()
    seen_ids: set[str] = set()
    duplicate_ids = 0

    for row_number, row in enumerate(rows, start=1):
        record, errors = validate_row(row)
        if record is not None:
            if record.record_id in seen_ids:
                errors = ["duplicate_record_id"]
                duplicate_ids += 1
            else:
                seen_ids.add(record.record_id)

        if errors:
            invalid.append(InvalidRecord(row_number=row_number, source=dict(row), errors=tuple(errors)))
            error_counts.update(errors)
        elif record is not None:
            clean.append(record)

    return clean, invalid, error_counts, duplicate_ids


def run_pipeline(input_path: Path, output_dir: Path) -> ProcessingReport:
    """Run the complete pipeline and write clean, invalid, and report outputs."""
    started = time.perf_counter()
    rows = read_records(input_path)
    clean, invalid, error_counts, duplicate_ids = process_records(rows)
    elapsed = time.perf_counter() - started

    output_dir.mkdir(parents=True, exist_ok=True)
    clean_path = output_dir / "clean.csv"
    invalid_path = output_dir / "invalid.json"
    report_path = output_dir / "report.json"

    write_csv(clean_path, (record.to_dict() for record in clean), CLEAN_FIELDS)
    write_json(invalid_path, [record.to_dict() for record in invalid])

    report = ProcessingReport(
        input_path=str(input_path),
        input_format=input_path.suffix.lower().lstrip("."),
        total_records=len(clean) + len(invalid),
        clean_records=len(clean),
        invalid_records=len(invalid),
        error_counts=dict(sorted(error_counts.items())),
        duplicate_ids=duplicate_ids,
        elapsed_seconds=round(elapsed, 6),
    )
    write_json(report_path, report.to_dict())
    return report
