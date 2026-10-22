"""Pipeline composition for sales records."""
from collections.abc import Iterable, Iterator

from processors import SalesRecord, filter_records, map_records


def add_total(record: SalesRecord) -> SalesRecord:
    """SalesRecord computes total_value as a property; keep it immutable."""
    return record


def build_pipeline(
    records: Iterable[SalesRecord],
    minimum_value: float = 100.0,
    category: str | None = None,
) -> Iterator[SalesRecord]:
    """Create a lazy filter/transform pipeline."""
    transformed = map_records(records, add_total)
    qualifying = filter_records(
        transformed,
        lambda record: record.total_value >= minimum_value,
    )
    if category is not None:
        qualifying = filter_records(
            qualifying,
            lambda record: record.category.casefold() == category.casefold(),
        )
    return qualifying
