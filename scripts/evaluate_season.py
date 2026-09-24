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
    parser.add_argument("--cutoffs", default="20,30,40", help="comma-separated cutoff laps")
    parser.add_argument("--output", default="artifacts/season_2024_evaluation.json")
    args = parser.parse_args()
    files = sorted(Path(args.directory).glob("*.parquet"))
    if len(files) < 2:
        raise SystemExit("At least two race parquet files are required")
    cutoffs = sorted({int(value.strip()) for value in args.cutoffs.split(",") if value.strip()})
    reports = []
    for test_file in files:
        test = pd.read_parquet(test_file)
        train_files = [file for file in files if file != test_file]
        training = pd.concat([pd.read_parquet(file) for file in train_files], ignore_index=True)
        for cutoff in cutoffs:
            try:
                report = evaluate_future_laps(test, cutoff, training)
            except ValueError:
                continue
            reports.append({"race": test_file.name, **report})
    primary = [report for report in reports if report["cutoff_lap"] == args.cutoff_lap]
    if not primary:
        raise SystemExit("The requested primary cutoff produced no valid reports")
    headline = {
        "headline": "future stint lap-time MAE on unseen races",
        "races": len(primary),
        "cutoff_lap": args.cutoff_lap,
        "test_laps": sum(report["test_laps"] for report in primary),
        "model_mae_seconds": round(sum(report["model_mae_seconds"] for report in primary) / len(primary), 3),
        "last_lap_baseline_mae_seconds": round(sum(report["last_lap_baseline_mae_seconds"] for report in primary) / len(primary), 3),
        "cutoff_metrics": {
            str(cutoff): {
                "races": len([r for r in reports if r["cutoff_lap"] == cutoff]),
                "model_mae_seconds": round(sum(r["model_mae_seconds"] for r in reports if r["cutoff_lap"] == cutoff) / max(1, len([r for r in reports if r["cutoff_lap"] == cutoff])), 3),
                "baseline_mae_seconds": round(sum(r["last_lap_baseline_mae_seconds"] for r in reports if r["cutoff_lap"] == cutoff) / max(1, len([r for r in reports if r["cutoff_lap"] == cutoff])), 3),
            } for cutoff in cutoffs
        },
    }
    payload = {"headline": headline, "races": reports}
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
