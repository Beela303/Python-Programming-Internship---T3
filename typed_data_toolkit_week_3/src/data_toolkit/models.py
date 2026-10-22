"""Typed data models shared by the pipeline."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class CleanRecord:
    """Canonical representation of a valid input row."""

    record_id: str
    name: str
    email: str
    age: int
    country: str

    def to_dict(self) -> dict[str, Any]:
        """Return a serialization-friendly mapping."""
        return asdict(self)


@dataclass(frozen=True, slots=True)
class InvalidRecord:
    """An input row that failed one or more validation rules."""

    row_number: int
    source: dict[str, Any]
    errors: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        """Return a serialization-friendly mapping."""
        return {
            "row_number": self.row_number,
            "source": self.source,
            "errors": list(self.errors),
        }


@dataclass(frozen=True, slots=True)
class ProcessingReport:
    """Summary metrics produced by a pipeline run."""

    input_path: str
    input_format: str
    total_records: int
    clean_records: int
    invalid_records: int
    error_counts: dict[str, int]
    duplicate_ids: int
    elapsed_seconds: float

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-ready report."""
        return asdict(self)
