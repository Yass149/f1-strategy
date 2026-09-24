"""Backtest the strategy baseline over a processed lap parquet file."""

import argparse
import json
from pathlib import Path

import pandas as pd

from race_engineer.backtest import backtest_strategy


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Processed lap parquet file")
    parser.add_argument("--output", default="artifacts/backtest.json")
    args = parser.parse_args()
    report = backtest_strategy(pd.read_parquet(args.input))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

