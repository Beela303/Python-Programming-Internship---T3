"""Command-line interface."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from data_toolkit.io import InputFormatError
from data_toolkit.pipeline import run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="data-toolkit",
        description="Validate and normalize CSV/JSON records into clean and invalid outputs.",
        epilog=(
            "Expected fields: record_id, name, email, age, country. "
            "The first valid occurrence of a record_id is kept; later duplicates are invalid."
        ),
    )
    parser.add_argument("input", type=Path, help="Input .csv or .json file")
    parser.add_argument("-o", "--output-dir", type=Path, default=Path("output"),
                        help="Directory for clean.csv, invalid.json, and report.json (default: output)")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report = run_pipeline(args.input, args.output_dir)
    except (OSError, InputFormatError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report.to_dict(), indent=2))
    print(f"\nWrote outputs to: {args.output_dir.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
