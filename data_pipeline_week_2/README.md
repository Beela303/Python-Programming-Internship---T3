# Reusable Python Data Processing Pipeline

An intermediate Python project demonstrating reusable data-processing components, eager versus lazy evaluation, safe resource management, and clean project structure.

## Learning objectives

- **First-class functions:** pass functions into reusable filtering and mapping components.
- **Lambda functions:** use small anonymous functions for simple predicates and sorting keys.
- **Decorators:** add timing, logging, and call-counting behavior without mixing it into core logic.
- **Iterators:** implement the iterator protocol with a reusable batch iterator.
- **Generators:** read CSV records and process results one item at a time.
- **Context managers:** ensure files close reliably, including when an error occurs.
- **Eager processing:** load records into lists when the dataset is small and convenient to reuse.
- **Lazy processing:** defer work until records are requested and avoid unnecessary intermediate lists.
- **Type hints and dataclasses:** make data structures and function contracts clearer.
- **Validation and error handling:** reject malformed records with useful error messages.
- **Unit testing:** check the behavior of reusable components.

## Project structure

```text
data_pipeline/
├── main.py
├── pipeline.py
├── readers.py
├── processors.py
├── decorators.py
├── README.md
├── data/
│   └── sales.csv
└── tests/
    └── test_pipeline.py
```

### Module responsibilities

| File | Responsibility |
|---|---|
| `main.py` | Application entry point; runs eager, lazy, and batch demonstrations. |
| `pipeline.py` | Composes reusable processing functions into a lazy pipeline. |
| `readers.py` | Opens CSV files safely and provides eager and lazy readers. |
| `processors.py` | Defines the sales record, validates input, filters/maps records, batches items, and calculates summaries. |
| `decorators.py` | Provides reusable logging, timing, and call-count decorators. |
| `data/sales.csv` | Sample sales data used by the application. |
| `tests/test_pipeline.py` | Unit tests for the main processing components. |

## Requirements

- Python 3.10 or newer.
- No third-party packages are required.

Check your Python version:

```bash
python --version
```

Depending on your system, you may need to use `python3` instead of `python`.

## Getting started

### 1. Run the application

```bash
python main.py
```

The program demonstrates:

1. **Eager processing:** reads all CSV records into memory, filters them, sorts qualifying sales by total value, and prints the results and summary.
2. **Lazy processing:** reads and filters records incrementally, then calculates a summary without retaining the complete result set.
3. **Batch processing:** reads records lazily and groups them into batches of three.

Logging output includes function calls and timing information. Exact execution times will vary by machine and workload.

### 3. Run the unit tests

From the project root:

```bash
python -m unittest discover -s tests -v
```

The tests cover filtering, pipeline thresholds, category filtering, summaries, batching, invalid batch sizes, and agreement between eager and lazy CSV readers.

## Sample data

The `data/sales.csv` file contains these columns:

| Column | Meaning | Example |
|---|---|---|
| `product` | Product name | `Laptop` |
| `category` | Product category | `Electronics` |
| `quantity` | Number of units sold | `2` |
| `price` | Price per unit | `750.00` |

The total value of a sale is calculated as:

```text
total_value = quantity * price
```

The sample pipeline uses a minimum total sale value of `100` by default. This is an illustrative threshold, not a currency-specific business rule.

## Eager versus lazy processing

### Eager processing

Eager processing builds a collection of results immediately. In this project, `read_all_records()` returns a list.

Use eager processing when:

- The dataset is small enough to fit comfortably in memory.
- You need to revisit the results multiple times.
- You need to sort the full result set.
- A list makes the code easier to understand.

### Lazy processing

Lazy processing yields records as they are requested. In this project, `iter_records()`, `map_records()`, and `filter_records()` use generators.

Use lazy processing when:

- The input is large.
- You can handle records incrementally.
- You want to avoid building unnecessary intermediate lists.
- You want to begin processing before reading the entire input.

### Important limitation

The lazy reader and pipeline do not automatically make every operation memory-constant. Sorting an entire dataset with `sorted()` requires collecting the records being sorted. The lazy demonstration avoids this by calculating a summary in one pass.

Lazy processing can reduce memory usage, but it is not guaranteed to be faster in every situation. Choose the approach that fits the workload and keeps the code clear.

## Key implementation ideas

### First-class functions

The processing helpers accept callables:

```python
filtered = filter_records(
    records,
    lambda record: record.total_value >= 100,
)
```

The filtering component does not need to know the business rule; callers supply it.

### Decorators

The timing and logging decorators wrap functions so that monitoring behavior can be reused without duplicating it inside every function.

### Iterators and batching

`BatchIterator` implements `__iter__()` and `__next__()`. It accepts any iterable, including a generator, and yields batches up to the configured size.

### Context managers

The CSV reader uses a `with` statement to ensure the file is closed when the block exits, including when an exception is raised.

### Validation

CSV values are converted to the expected types and validated. Invalid records raise a `ValueError` that includes the CSV line number.

The current application stops on an invalid record. A production importer might instead log rejected rows and continue processing valid ones.