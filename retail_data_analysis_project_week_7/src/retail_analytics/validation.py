import pandas as pd

REQUIRED_COLUMNS = {
    "order_id", "customer_id", "product_id", "order_date", "quantity",
    "unit_price", "discount_rate", "customer_name", "region",
    "product_name", "category", "unit_cost", "net_sales", "gross_profit",
}

def validate_dataset(frame: pd.DataFrame) -> dict:
    checks = {
        "required_columns_present": REQUIRED_COLUMNS.issubset(frame.columns),
        "no_duplicate_order_lines": not frame.duplicated(["order_id", "product_id"]).any(),
        "positive_quantities": bool((frame["quantity"] > 0).all()),
        "non_negative_prices": bool((frame["unit_price"] >= 0).all()),
        "discounts_in_valid_range": bool(frame["discount_rate"].between(0, 1, inclusive="left").all()),
        "derived_sales_non_negative": bool((frame["net_sales"] >= 0).all()),
        "join_dimensions_populated": bool(frame[["customer_name", "product_name", "category", "region"]].notna().all().all()),
    }
    return {"passed": all(checks.values()), "checks": checks, "row_count": int(len(frame))}
