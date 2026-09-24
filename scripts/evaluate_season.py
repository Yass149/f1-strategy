"""Evaluate each race as an unseen test race against the other files."""

import argparse
import json
from pathlib import Path

import pandas as pd

from race_engineer.race_backtest import evaluate_future_laps


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", default="data/processed", nargs="?")
    parser.add_argument("--cutoff-lap", type=int, default=20)
    parser.add_argument("--output", default="artifacts/season_evaluation.json")
    args = parser.parse_args()
    files = sorted(Path(args.directory).glob("*.parquet"))
    if len(files) < 2:
        raise SystemExit("At least two race parquet files are required")
    reports = []
    for test_file in files:
        test = pd.read_parquet(test_file)
        train_files = [file for file in files if file != test_file]
        training = pd.concat([pd.read_parquet(file) for file in train_files], ignore_index=True)
        reports.append({"race": test_file.name, **evaluate_future_laps(test, args.cutoff_lap, training)})
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(reports, indent=2) + "\n")
    print(json.dumps(reports, indent=2))


if __name__ == "__main__":
    main()
