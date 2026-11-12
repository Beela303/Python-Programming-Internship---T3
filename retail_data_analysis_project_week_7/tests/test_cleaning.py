import pandas as pd
from retail_analytics.cleaning import clean_orders, normalise_columns

def test_normalise_columns():
    frame = normalise_columns(pd.DataFrame({"Order Date ": ["2026-01-01"], "Unit Price($)": [2]}))
    assert list(frame.columns) == ["order_date", "unit_price"]

def test_missing_discount_is_filled_and_bad_quantity_rejected():
    frame = pd.DataFrame([
        {"Order ID": "A", "Customer ID": "C1", "Product ID": "P1", "Order Date": "2026-01-01",
         "Quantity": 2, "Unit Price": 10, "Discount Rate": None},
        {"Order ID": "B", "Customer ID": "C1", "Product ID": "P1", "Order Date": "2026-01-01",
         "Quantity": 0, "Unit Price": 10, "Discount Rate": 0},
    ])
    accepted, rejected, audit = clean_orders(frame)
    assert len(accepted) == 1
    assert accepted.iloc[0]["discount_rate"] == 0
    assert len(rejected) == 1
    assert "invalid_quantity" in rejected.iloc[0]["rejection_reason"]
    assert audit["missing_discounts_filled_with_zero"] == 1
