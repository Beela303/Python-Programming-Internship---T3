import json
from pathlib import Path
from retail_analytics.pipeline import run_pipeline

def test_pipeline_outputs_and_validation():
    root = Path(__file__).resolve().parents[1]
    result = run_pipeline(root)
    assert result["validation"]["passed"]
    assert result["accepted_rows"] > 0
    assert (root / "data/processed/validated_sales.csv").exists()
    audit = json.loads((root / "data/processed/cleaning_audit.json").read_text())
    assert audit["source_order_rows"] > audit["accepted_rows"]
    assert (root / "exports/findings.md").exists()
