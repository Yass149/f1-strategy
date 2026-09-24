"""Fit tyre degradation coefficients from a processed lap parquet file."""

import argparse
import json
from pathlib import Path

import pandas as pd

from race_engineer.degradation import TyreDegradationModel


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Processed lap parquet file")
    parser.add_argument("--output", default="artifacts/degradation.json")
    args = parser.parse_args()

    model = TyreDegradationModel().fit(pd.read_parquet(args.input))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(model.to_dict(), indent=2) + "\n")
    print(f"Wrote degradation fits to {output}")


if __name__ == "__main__":
    main()

