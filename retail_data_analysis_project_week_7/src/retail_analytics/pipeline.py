from pathlib import Path
from datetime import datetime, timezone
import json
import pandas as pd
from .config import project_paths
from .io import load_inputs, sha256_file
from .cleaning import prepare_dimensions, clean_orders, join_and_derive
from .validation import validate_dataset
from .analysis import build_summaries, write_findings

def run_pipeline(root: Path) -> dict:
    paths = project_paths(root)
    paths["processed"].mkdir(parents=True, exist_ok=True)
    paths["exports"].mkdir(parents=True, exist_ok=True)
    raw = load_inputs(paths["raw"])

    customers, products = prepare_dimensions(raw["customers"], raw["products"])
    orders, rejected_prejoin, audit = clean_orders(raw["orders"])
    dataset, rejected_join = join_and_derive(orders, customers, products)
    rejected = pd.concat([rejected_prejoin, rejected_join], ignore_index=True, sort=False)

    validation = validate_dataset(dataset)
    if not validation["passed"]:
        raise ValueError(f"Dataset validation failed: {validation['checks']}")

    dataset.to_csv(paths["processed"] / "validated_sales.csv", index=False, date_format="%Y-%m-%d")
    rejected.to_csv(paths["processed"] / "rejected_orders.csv", index=False)
    audit.update({
        "accepted_rows": int(len(dataset)),
        "rejected_total": int(len(rejected)),
        "raw_customer_rows": int(len(raw["customers"])),
        "raw_product_rows": int(len(raw["products"])),
        "cleaning_policy": {
            "missing_discount": "filled with 0.0",
            "missing_customer_name": "filled with Unknown customer",
            "missing_region": "filled with Unknown",
            "missing_product_name": "filled with Unknown product",
            "missing_category": "filled with Uncategorised",
            "invalid_critical_fields": "rejected with reason",
            "unmatched_dimension_keys": "rejected with reason",
        },
    })
    (paths["processed"] / "cleaning_audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
    (paths["processed"] / "validation_report.json").write_text(json.dumps(validation, indent=2), encoding="utf-8")

    summaries = build_summaries(dataset)
    for name, summary in summaries.items():
        summary.to_csv(paths["exports"] / f"{name}.csv", index=False, float_format="%.4f")
    write_findings(dataset, summaries, paths["exports"] / "findings.md")

    manifest = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "pipeline": "retail_analytics",
        "input_sha256": {name: sha256_file(paths["raw"] / f"{name}.csv") for name in raw},
        "accepted_rows": int(len(dataset)),
        "rejected_rows": int(len(rejected)),
        "validation_passed": validation["passed"],
    }
    (paths["exports"] / "run_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return {"accepted_rows": len(dataset), "rejected_rows": len(rejected), "validation": validation}
