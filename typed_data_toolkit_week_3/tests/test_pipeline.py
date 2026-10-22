import csv
import json
from pathlib import Path

from data_toolkit.pipeline import normalize_row, process_records, run_pipeline, validate_row


def valid_row(**overrides):
    row = {
        "record_id": "A-1",
        "name": "  Ada   Lovelace ",
        "email": "ADA@EXAMPLE.COM",
        "age": "36",
        "country": " united kingdom ",
    }
    row.update(overrides)
    return row


def test_normalize_row_trims_and_standardizes_text():
    result = normalize_row(valid_row())
    assert result["name"] == "Ada Lovelace"
    assert result["email"] == "ada@example.com"
    assert result["country"] == "United Kingdom"


def test_valid_row_becomes_typed_dataclass():
    record, errors = validate_row(valid_row())
    assert errors == []
    assert record is not None
    assert record.age == 36
    assert isinstance(record.age, int)


def test_invalid_email_and_age_are_reported():
    record, errors = validate_row(valid_row(email="not-an-email", age="999"))
    assert record is None
    assert "invalid_email:expected_name_at_domain" in errors
    assert "invalid_age:must_be_between_0_and_120" in errors


def test_missing_fields_are_reported():
    record, errors = validate_row({"record_id": "A"})
    assert record is None
    assert "missing_required_field:name" in errors
    assert "missing_required_field:email" in errors


def test_duplicate_id_keeps_first_valid_row():
    rows = [valid_row(), valid_row(name="Second person")]
    clean, invalid, counts, duplicates = process_records(rows)
    assert len(clean) == 1
    assert len(invalid) == 1
    assert invalid[0].errors == ("duplicate_record_id",)
    assert counts["duplicate_record_id"] == 1
    assert duplicates == 1


def test_pipeline_writes_clean_invalid_and_report(tmp_path: Path):
    source = tmp_path / "people.csv"
    with source.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["record_id", "name", "email", "age", "country"])
        writer.writeheader()
        writer.writerow(valid_row())
        writer.writerow(valid_row(record_id="A-2", email="bad"))
    out = tmp_path / "out"

    report = run_pipeline(source, out)

    assert report.total_records == 2
    assert report.clean_records == 1
    assert report.invalid_records == 1
    assert (out / "clean.csv").exists()
    assert (out / "invalid.json").exists()
    assert (out / "report.json").exists()
    invalid = json.loads((out / "invalid.json").read_text(encoding="utf-8"))
    assert "invalid_email:expected_name_at_domain" in invalid[0]["errors"]


def test_json_non_object_item_is_reported_as_invalid(tmp_path: Path):
    source = tmp_path / "people.json"
    source.write_text(json.dumps([valid_row(), "not-an-object"]), encoding="utf-8")
    out = tmp_path / "out"
    report = run_pipeline(source, out)
    assert report.total_records == 2
    assert report.clean_records == 1
    assert report.invalid_records == 1
