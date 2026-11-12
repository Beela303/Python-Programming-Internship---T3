from pathlib import Path
import pandas as pd

def build_summaries(data: pd.DataFrame) -> dict[str, pd.DataFrame]:
    category = (data.groupby("category", as_index=False)
        .agg(order_lines=("order_id", "size"), units_sold=("quantity", "sum"),
             net_sales=("net_sales", "sum"), gross_profit=("gross_profit", "sum")))
    category["gross_margin_rate"] = category["gross_profit"].div(category["net_sales"]).where(category["net_sales"].ne(0), 0)
    category = category.sort_values("net_sales", ascending=False)

    region = (data.groupby("region", as_index=False)
        .agg(order_lines=("order_id", "size"), net_sales=("net_sales", "sum"),
             gross_profit=("gross_profit", "sum"))
        .sort_values("net_sales", ascending=False))

    monthly = (data.groupby("order_month", as_index=False)
        .agg(order_lines=("order_id", "size"), units_sold=("quantity", "sum"),
             net_sales=("net_sales", "sum"), gross_profit=("gross_profit", "sum"))
        .sort_values("order_month"))
    return {"category_summary": category, "region_summary": region, "monthly_summary": monthly}

def write_findings(data: pd.DataFrame, summaries: dict[str, pd.DataFrame], path: Path):
    total_sales = float(data["net_sales"].sum())
    total_profit = float(data["gross_profit"].sum())
    margin = total_profit / total_sales if total_sales else 0.0
    top = summaries["category_summary"].iloc[0] if not summaries["category_summary"].empty else None
    month = summaries["monthly_summary"].sort_values("net_sales", ascending=False).iloc[0] if not summaries["monthly_summary"].empty else None
    lines = [
        "# Analytical findings",
        "",
        f"- The validated dataset contains **{len(data):,} order lines**.",
        f"- Net sales total **{total_sales:,.2f}** fictional currency units.",
        f"- Gross profit totals **{total_profit:,.2f}**, giving an overall gross margin of **{margin:.1%}**.",
    ]
    if top is not None:
        lines.append(f"- **{top['category']}** is the highest-sales category at **{top['net_sales']:,.2f}**.")
    if month is not None:
        lines.append(f"- **{month['order_month']}** is the highest-sales month at **{month['net_sales']:,.2f}**.")
    lines += ["", "## Interpretation notes", "",
              "These findings describe accepted rows in the supplied fictional sample only. "
              "Review `cleaning_audit.json`, `validation_report.json`, and `rejected_orders.csv` "
              "before sharing results. Totals are not forecasts and do not establish causation."]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
