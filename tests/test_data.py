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
