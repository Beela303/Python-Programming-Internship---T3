from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from retail_analytics.pipeline import run_pipeline

if __name__ == "__main__":
    result = run_pipeline(ROOT)
    print(f"Pipeline complete: {result['accepted_rows']} accepted rows; "
          f"{result['rejected_rows']} rejected rows.")
    print(f"Findings: {ROOT / 'exports' / 'findings.md'}")
