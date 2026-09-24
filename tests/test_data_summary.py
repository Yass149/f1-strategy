import pandas as pd

from race_engineer.data import summarise_lap_file


def test_summary_reports_missing_file(tmp_path) -> None:
    summary = summarise_lap_file(tmp_path / "missing.parquet")
    assert summary["available"] is False


def test_summary_reports_processed_laps(tmp_path) -> None:
    path = tmp_path / "laps.parquet"
    pd.DataFrame({"driver": ["HAM", "VER"], "lap_number": [1, 57]}).to_parquet(path)
    summary = summarise_lap_file(path)
    assert summary == {
        "available": True,
        "path": str(path),
        "lap_count": 2,
        "driver_count": 2,
        "drivers": ["HAM", "VER"],
        "lap_min": 1,
        "lap_max": 57,
    }
