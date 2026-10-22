"""Run the eager, lazy and batch processing demonstrations."""
import logging
from pathlib import Path

from decorators import log_call, measure_time
from pipeline import build_pipeline
from processors import BatchIterator, SalesRecord, summarize
from readers import iter_records, read_all_records

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "sales.csv"

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


@measure_time
@log_call
def run_eager(file_path: Path) -> None:
    print("\\n=== EAGER PROCESSING ===")
    records = read_all_records(file_path)
    # The pipeline is lazy, but list() deliberately materializes its results.
    selected = list(build_pipeline(records, minimum_value=100))
    selected.sort(key=lambda record: record.total_value, reverse=True)
    for record in selected:
        print(
            f"{record.product:10} | {record.category:12} | "
            f"qty={record.quantity:2} | total={record.total_value:8.2f}"
        )
    print("Summary:", summarize(selected))


@measure_time
@log_call
def run_lazy(file_path: Path) -> None:
    print("\\n=== LAZY PROCESSING (streaming summary) ===")
    # No list and no sorting: records are consumed one at a time.
    selected = build_pipeline(iter_records(file_path), minimum_value=100)
    print("Summary:", summarize(selected))


def run_batches(file_path: Path) -> None:
    print("\\n=== BATCH PROCESSING ===")
    batches = BatchIterator(iter_records(file_path), batch_size=3)
    for number, batch in enumerate(batches, start=1):
        names = ", ".join(record.product for record in batch)
        print(f"Batch {number}: {names}")


def main() -> int:
    if not DATA_FILE.is_file():
        logger.error("CSV file not found: %s", DATA_FILE)
        return 1

    try:
        run_eager(DATA_FILE)
        run_lazy(DATA_FILE)
        run_batches(DATA_FILE)
    except (OSError, ValueError) as error:
        logger.error("Processing failed: %s", error)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
