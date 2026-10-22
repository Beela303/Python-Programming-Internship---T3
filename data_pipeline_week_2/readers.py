"""Safe, eager and lazy readers for sales CSV files."""
import csv
from contextlib import contextmanager
from pathlib import Path
from collections.abc import Iterator
from typing import TextIO

from processors import SalesRecord, parse_record


@contextmanager
def open_csv_file(file_path: Path) -> Iterator[TextIO]:
    """Open a text CSV file and guarantee it is closed."""
    with file_path.open("r", encoding="utf-8", newline="") as handle:
        yield handle


def read_all_records(file_path: Path) -> list[SalesRecord]:
    """Read every valid record into memory (eager processing)."""
    with open_csv_file(file_path) as handle:
        reader = csv.DictReader(handle)
        return [parse_record(row, line_number=index)
                for index, row in enumerate(reader, start=2)]


def iter_records(file_path: Path) -> Iterator[SalesRecord]:
    """Yield valid records one at a time (lazy processing)."""
    with open_csv_file(file_path) as handle:
        reader = csv.DictReader(handle)
        for index, row in enumerate(reader, start=2):
            yield parse_record(row, line_number=index)
