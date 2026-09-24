import pandas as pd
import pytest

from race_engineer.data import build_lap_features


def test_build_lap_features_converts_timedeltas_and_sorts_by_driver() -> None:
    laps = pd.DataFrame(
        {
            "Driver": ["HAM", "VER", "HAM"],
            "LapNumber": [2, 1, 1],
            "LapTime": pd.to_timedelta([91.5, 90.2, 92.0], unit="s"),
            "Compound": ["MEDIUM", "SOFT", "MEDIUM"],
            "TyreLife": [2, 1, 1],
            "IsAccurate": [True, True, False],
        }
    )
    features = build_lap_features(laps)
    assert features["driver"].tolist() == ["HAM"]
    assert features["lap_time_seconds"].tolist() == [91.5]


def test_build_lap_features_requires_core_columns() -> None:
    with pytest.raises(ValueError, match="Lap table is missing"):
        build_lap_features(pd.DataFrame({"Driver": ["HAM"]}))


def test_weather_join_is_backward_looking() -> None:
    from race_engineer.data import attach_weather_features

    laps = pd.DataFrame({"lap_end_time": pd.to_datetime(["2024-01-01 00:01:00", "2024-01-01 00:03:00"], utc=True)})
    weather = pd.DataFrame({"Time": pd.to_datetime(["2024-01-01 00:02:00", "2024-01-01 00:04:00"], utc=True), "TrackTemp": [30.0, 40.0]})
    joined = attach_weather_features(laps, weather)
    assert pd.isna(joined.iloc[0]["TrackTemp"])
    assert joined.iloc[1]["TrackTemp"] == 30.0
