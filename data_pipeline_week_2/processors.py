"""Reusable transformations, filters, iterators and summaries."""
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass
from typing import TypeVar

T = TypeVar("T")
U = TypeVar("U")


@dataclass(frozen=True)
class SalesRecord:
    product: str
    category: str
    quantity: int
    price: float

    @property
    def total_value(self) -> float:
        return self.quantity * self.price


def parse_record(row: dict[str, str], line_number: int = 0) -> SalesRecord:
    """Validate and convert one CSV row into a SalesRecord."""
    try:
        product = row["product"].strip()
        category = row["category"].strip()
        quantity = int(row["quantity"])
        price = float(row["price"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(
            f"Invalid sales data on CSV line {line_number}: {row!r}"
        ) from exc

    if not product or not category:
        raise ValueError(
            f"Product and category cannot be empty (line {line_number})."
        )
    if quantity < 0 or price < 0:
        raise ValueError(
            f"Quantity and price cannot be negative (line {line_number})."
        )
    return SalesRecord(product, category, quantity, price)


def filter_records(
    records: Iterable[T],
    predicate: Callable[[T], bool],
) -> Iterator[T]:
    """Yield only records for which predicate returns True."""
    for record in records:
        if predicate(record):
            yield record


def map_records(
    records: Iterable[T],
    transform: Callable[[T], U],
) -> Iterator[U]:
    """Apply a transformation lazily to each item."""
    for record in records:
        yield transform(record)


class BatchIterator(Iterator[list[T]]):
    """Yield fixed-size lists from any iterable, including generators."""

    def __init__(self, items: Iterable[T], batch_size: int) -> None:
        if batch_size <= 0:
            raise ValueError("batch_size must be greater than zero.")
        self._items = iter(items)
        self._batch_size = batch_size

    def __iter__(self) -> "BatchIterator[T]":
        return self

    def __next__(self) -> list[T]:
        batch: list[T] = []
        for _ in range(self._batch_size):
            try:
                batch.append(next(self._items))
            except StopIteration:
                break
        if not batch:
            raise StopIteration
        return batch


def summarize(records: Iterable[SalesRecord]) -> dict[str, int | float]:
    """Calculate count, revenue and highest sale in a single pass."""
    count = 0
    total_revenue = 0.0
    highest_sale = 0.0

    for record in records:
        count += 1
        total_revenue += record.total_value
        highest_sale = max(highest_sale, record.total_value)

    return {
        "count": count,
        "total_revenue": total_revenue,
        "highest_sale": highest_sale,
    }
