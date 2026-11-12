import pandas as pd
import numpy as np

def normalise_columns(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    result.columns = (result.columns.astype(str).str.strip().str.lower()
                      .str.replace(r"[^a-z0-9]+", "_", regex=True)
                      .str.strip("_"))
    return result

def prepare_dimensions(customers: pd.DataFrame, products: pd.DataFrame):
    customers = normalise_columns(customers)
    products = normalise_columns(products)
    customers["customer_id"] = customers["customer_id"].astype("string").str.strip()
    products["product_id"] = products["product_id"].astype("string").str.strip()
    customers["customer_name"] = customers["customer_name"].fillna("Unknown customer").astype(str).str.strip()
    customers["region"] = customers["region"].fillna("Unknown").astype(str).str.strip()
    products["product_name"] = products["product_name"].fillna("Unknown product").astype(str).str.strip()
    products["category"] = products["category"].fillna("Uncategorised").astype(str).str.strip()
    products["unit_cost"] = pd.to_numeric(products["unit_cost"], errors="coerce")
    return customers.drop_duplicates("customer_id"), products.drop_duplicates("product_id")

def clean_orders(orders: pd.DataFrame):
    frame = normalise_columns(orders)
    source_rows = len(frame)
    duplicate_mask = frame.duplicated(keep="first")
    duplicates_removed = int(duplicate_mask.sum())
    frame = frame.loc[~duplicate_mask].copy()

    frame["order_id"] = frame["order_id"].astype("string").str.strip()
    frame["customer_id"] = frame["customer_id"].astype("string").str.strip()
    frame["product_id"] = frame["product_id"].astype("string").str.strip()
    frame["order_date"] = pd.to_datetime(frame["order_date"], errors="coerce")
    for column in ["quantity", "unit_price", "discount_rate"]:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")

    # Missing discounts mean no discount; all other critical fields must validate.
    missing_discount_count = int(frame["discount_rate"].isna().sum())
    frame["discount_rate"] = frame["discount_rate"].fillna(0.0)

    reasons = pd.Series("", index=frame.index, dtype="string")
    def mark(mask, reason):
        nonlocal reasons
        reasons = reasons.mask(mask, reasons + reason + "; ")

    mark(frame["order_id"].isna() | frame["order_id"].eq(""), "missing_order_id")
    mark(frame["customer_id"].isna() | frame["customer_id"].eq(""), "missing_customer_id")
    mark(frame["product_id"].isna() | frame["product_id"].eq(""), "missing_product_id")
    mark(frame["order_date"].isna(), "invalid_order_date")
    mark(frame["quantity"].isna() | (frame["quantity"] <= 0), "invalid_quantity")
    mark(frame["unit_price"].isna() | (frame["unit_price"] < 0), "invalid_unit_price")
    mark((frame["discount_rate"] < 0) | (frame["discount_rate"] >= 1), "invalid_discount_rate")

    rejected = frame.loc[reasons.ne("")].copy()
    rejected["rejection_reason"] = reasons.loc[reasons.ne("")].str.rstrip("; ")
    accepted = frame.loc[reasons.eq("")].copy()

    audit = {
        "source_order_rows": source_rows,
        "exact_duplicates_removed": duplicates_removed,
        "missing_discounts_filled_with_zero": missing_discount_count,
        "rejected_before_join": len(rejected),
    }
    return accepted, rejected, audit

def join_and_derive(orders, customers, products):
    merged = orders.merge(customers, on="customer_id", how="left", validate="many_to_one", indicator="customer_match")
    merged = merged.merge(products, on="product_id", how="left", validate="many_to_one", indicator="product_match", suffixes=("", "_product"))
    unmatched = merged["customer_match"].ne("both") | merged["product_match"].ne("both")
    rejected = merged.loc[unmatched].copy()
    if not rejected.empty:
        rejected["rejection_reason"] = np.where(
            rejected["customer_match"].ne("both") & rejected["product_match"].ne("both"),
            "unmatched_customer_and_product",
            np.where(rejected["customer_match"].ne("both"), "unmatched_customer", "unmatched_product")
        )
    valid = merged.loc[~unmatched].drop(columns=["customer_match", "product_match"]).copy()
    valid["unit_cost"] = pd.to_numeric(valid["unit_cost"], errors="coerce")
    bad_cost = valid["unit_cost"].isna() | (valid["unit_cost"] < 0)
    if bad_cost.any():
        extra = valid.loc[bad_cost].copy()
        extra["rejection_reason"] = "missing_or_invalid_unit_cost"
        rejected = pd.concat([rejected, extra], ignore_index=True, sort=False)
        valid = valid.loc[~bad_cost].copy()

    quantity = valid["quantity"].to_numpy(dtype=float)
    price = valid["unit_price"].to_numpy(dtype=float)
    discount = valid["discount_rate"].to_numpy(dtype=float)
    cost = valid["unit_cost"].to_numpy(dtype=float)
    valid["gross_sales"] = np.round(quantity * price, 2)
    valid["net_sales"] = np.round(quantity * price * (1 - discount), 2)
    valid["total_cost"] = np.round(quantity * cost, 2)
    valid["gross_profit"] = np.round(valid["net_sales"] - valid["total_cost"], 2)
    valid["gross_margin_rate"] = np.divide(
        valid["gross_profit"].to_numpy(),
        valid["net_sales"].to_numpy(),
        out=np.zeros(len(valid), dtype=float),
        where=valid["net_sales"].to_numpy() != 0,
    )
    valid["order_month"] = valid["order_date"].dt.to_period("M").astype(str)
    valid["revenue_band"] = np.select(
        [valid["net_sales"] < 100, valid["net_sales"] < 500],
        ["under_100", "100_to_499_99"],
        default="500_plus",
    )
    return valid, rejected
