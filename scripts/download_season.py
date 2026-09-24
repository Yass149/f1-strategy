"""Download and process every race session in a season."""

import argparse
from pathlib import Path

from race_engineer.data import build_lap_features, load_session


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, default=2024)
    parser.add_argument("--output-dir", default="data/processed")
    parser.add_argument("--refresh", action="store_true", help="rebuild existing parquet files")
    args = parser.parse_args()
    import fastf1

    schedule = fastf1.get_event_schedule(args.year, include_testing=False)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    for _, event in schedule.iterrows():
        round_number = int(event["RoundNumber"])
        if round_number <= 0:
            continue
        name = str(event["EventName"]).lower().replace(" ", "_")
        output = output_dir / f"{args.year}_{round_number:02d}_{name}.parquet"
        if output.exists() and not args.refresh:
            print(f"Skipping cached {output}")
            continue
        session = load_session(args.year, round_number, "R")
        build_lap_features(session.laps, session.weather_data).to_parquet(output, index=False)
        print(f"Wrote {output}")


if __name__ == "__main__":
    main()

