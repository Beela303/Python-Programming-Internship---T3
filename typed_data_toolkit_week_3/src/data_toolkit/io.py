"""Input and output helpers for CSV and JSON."""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable, Iterator

Row = dict[str, Any]


class InputFormatError(ValueError):
    """Raised when an input file cannot be interpreted as CSV or JSON."""


def infer_format(path: Path) -> str:
    """Infer supported format from a file extension."""
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return "csv"
    if suffix == ".json":
        return "json"
    raise InputFormatError(f"Unsupported file extension '{suffix}'. Use .csv or .json.")


def read_records(path: Path) -> Iterator[Row]:
    """Stream CSV rows; load JSON arrays and yield object rows."""
    file_format = infer_format(path)
    if not path.exists():
        raise FileNotFoundError(f"Input file does not exist: {path}")

    if file_format == "csv":
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                raise InputFormatError("CSV input is empty or has no header row.")
            yield from (dict(row) for row in reader)
        return

    try:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except json.JSONDecodeError as exc:
        raise InputFormatError(f"Invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}") from exc

    if not isinstance(payload, list):
        raise InputFormatError("JSON input must be an array of objects.")
    for index, item in enumerate(payload, start=1):
        if not isinstance(item, dict):
            yield {"__input_error__": f"JSON item {index} is not an object", "__raw__": item}
        else:
            yield dict(item)


def write_csv(path: Path, records: Iterable[dict[str, Any]], fieldnames: list[str]) -> None:
    """Write records to a CSV file, including a header for empty results."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)


def write_json(path: Path, value: Any) -> None:
    """Write JSON with stable indentation and UTF-8 encoding."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
