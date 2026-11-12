# Retail Sales Data Analysis — NumPy & pandas

An project that turns deliberately messy retail CSV files into a validated analytical dataset, reproducible summaries, and auditable exports.

## What it demonstrates

- Loading multiple tabular sources with pandas.
- Cleaning column names, types, duplicates, invalid values, and missing values.
- Joining orders to customer and product dimensions.
- NumPy vectorised calculations (line revenue, discounts, margin, and revenue bands).
- Grouping and summarising by product category, region, and month.
- Validation rules with explicit error reports.
- Audit outputs: source row counts, rejected rows, missing-value treatment, and pipeline run metadata.
- Separation of exploratory analysis (`notebooks/exploration.py`) from repeatable production code (`src/retail_analytics/`).
- Automated tests using pytest.

## Project structure

```text
retail_data_analysis_project/
├── data/
│   ├── raw/                  # Original, intentionally imperfect CSV inputs
│   └── processed/            # Generated validated dataset and audit files
├── exports/                  # Generated summaries and findings
├── notebooks/
│   └── exploration.py        # Ad-hoc exploration; not used by the pipeline
├── src/retail_analytics/
│   ├── __init__.py
│   ├── config.py
│   ├── io.py
│   ├── cleaning.py
│   ├── validation.py
│   ├── analysis.py
│   └── pipeline.py
├── tests/
├── requirements.txt
└── run_pipeline.py
```

## Dataset

The project uses a fictional retail business. The raw inputs are:

- `orders.csv`: order lines, dates, quantities, unit prices, discounts, and customer/product keys.
- `customers.csv`: customer names and sales regions.
- `products.csv`: product names, categories, and unit costs.

The raw files intentionally include duplicate order lines, missing values, malformed dates, invalid quantities, and unmatched foreign keys. These are teaching examples, not real customer data.

## Setup

Python 3.10+ is recommended.

```bash
python -m venv .venv
```

Activate it:

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Run the repeatable pipeline

From the project root:

```bash
python run_pipeline.py
```

The pipeline reads only from `data/raw/` and writes deterministic outputs to `data/processed/` and `exports/`. It does not modify the raw inputs.

### Main outputs

| Output | Purpose |
|---|---|
| `data/processed/validated_sales.csv` | Validated, joined, analysis-ready order lines |
| `data/processed/rejected_orders.csv` | Rows excluded from analysis, with rejection reasons |
| `data/processed/cleaning_audit.json` | Input/output row counts and cleaning decisions |
| `data/processed/validation_report.json` | Validation checks and results |
| `exports/category_summary.csv` | Sales and margin by product category |
| `exports/region_summary.csv` | Sales by customer region |
| `exports/monthly_summary.csv` | Monthly sales trend |
| `exports/findings.md` | Plain-language findings generated from the data |
| `exports/run_manifest.json` | Run timestamp, source file hashes, and output row count |

All money values are represented in the dataset's fictional currency units. The pipeline does not assume a real-world currency.

## Data quality policy

1. Column names are normalised to lowercase snake_case.
2. Exact duplicate order rows are removed; the audit records how many were removed.
3. Dates are parsed strictly. Unparseable dates are rejected.
4. Missing or non-positive quantities, negative prices/costs, and missing join keys are rejected.
5. Missing discounts are filled with `0.0`; discounts outside `[0, 1)` are rejected.
6. Missing customer region is filled with `Unknown`; missing customer name is filled with `Unknown customer`.
7. Missing product category/name are filled with `Uncategorised` / `Unknown product`.
8. Unmatched customer or product keys are rejected rather than silently dropped.
9. Derived values are calculated after validation with vectorised NumPy/pandas operations.

## Key metrics

- **Gross sales:** quantity × unit price.
- **Net sales:** gross sales × (1 − discount rate).
- **Cost:** quantity × unit cost.
- **Gross profit:** net sales − cost.
- **Gross margin rate:** gross profit ÷ net sales; zero when net sales are zero.

The analysis uses groupby aggregations, not row-by-row Python loops.

## Run tests

```bash
pytest -q
```