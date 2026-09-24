"""Download one cached FastF1 session and write its lap feature table."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Union

from race_engineer.data import build_lap_features, load_session


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--event", required=True, help="Round number or event name")
    parser.add_argument("--session", default="R", choices=["R", "Q", "S", "FP1", "FP2", "FP3"])
    parser.add_argument("--output", default="data/processed/laps.parquet")
    args = parser.parse_args()

    event: Union[str, int] = int(args.event) if args.event.isdigit() else args.event
    session = load_session(args.year, event, args.session)
    features = build_lap_features(session.laps)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    features.to_parquet(output, index=False)
    print(f"Wrote {len(features):,} laps to {output}")


if __name__ == "__main__":
    main()
