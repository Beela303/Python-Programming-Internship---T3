"""Unit tests for the reusable processing components."""
import tempfile
import unittest
from pathlib import Path

from pipeline import build_pipeline
from processors import BatchIterator, SalesRecord, filter_records, summarize
from readers import iter_records, read_all_records


class ProcessingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.records = [
            SalesRecord("Laptop", "Electronics", 2, 750.0),
            SalesRecord("Mouse", "Electronics", 10, 15.0),
            SalesRecord("Chair", "Furniture", 4, 85.0),
        ]

    def test_filter_records(self) -> None:
        result = list(filter_records(self.records, lambda r: r.quantity >= 4))
        self.assertEqual([r.product for r in result], ["Mouse", "Chair"])

    def test_pipeline_threshold(self) -> None:
        result = list(build_pipeline(self.records, minimum_value=100))
        self.assertEqual([r.product for r in result], ["Laptop", "Mouse", "Chair"])

    def test_pipeline_category(self) -> None:
        result = list(
            build_pipeline(self.records, minimum_value=0, category="electronics")
        )
        self.assertEqual([r.product for r in result], ["Laptop", "Mouse"])

    def test_summary(self) -> None:
        result = summarize(self.records)
        self.assertEqual(result["count"], 3)
        self.assertAlmostEqual(result["total_revenue"], 1990.0)
        self.assertAlmostEqual(result["highest_sale"], 1500.0)

    def test_batches(self) -> None:
        batches = list(BatchIterator(iter(range(7)), batch_size=3))
        self.assertEqual(batches, [[0, 1, 2], [3, 4, 5], [6]])

    def test_invalid_batch_size(self) -> None:
        with self.assertRaises(ValueError):
            BatchIterator([1, 2], batch_size=0)

    def test_eager_and_lazy_readers_match(self) -> None:
        content = (
            "product,category,quantity,price\\n"
            "Pen,Stationery,2,3.5\\n"
            "Book,Stationery,4,10.0\\n"
        )
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "sales.csv"
            path.write_text(content, encoding="utf-8")
            self.assertEqual(read_all_records(path), list(iter_records(path)))


if __name__ == "__main__":
    unittest.main()
