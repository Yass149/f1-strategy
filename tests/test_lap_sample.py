import pandas as pd

from race_engineer.data import read_lap_sample


def test_read_lap_sample_filters_driver_and_limits_rows(tmp_path) -> None:
    path = tmp_path / "laps.parquet"
    pd.DataFrame(
        {
            "driver": ["VER", "HAM", "VER"],
            "lap_number": [1, 1, 2],
            "lap_time_seconds": [90.1, 91.0, 89.9],
            "tyre_life": [1, 1, 2],
            "compound": ["MEDIUM", "HARD", "MEDIUM"],
        }
    ).to_parquet(path)
    sample = read_lap_sample(path, driver="VER", limit=1)
    assert len(sample) == 1
    assert sample[0]["driver"] == "VER"

