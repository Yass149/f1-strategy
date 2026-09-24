import pandas as pd
import pytest

from race_engineer.degradation import TyreDegradationModel


def test_model_recovers_interpretable_degradation_line() -> None:
    laps = pd.DataFrame(
        {
            "compound": ["MEDIUM"] * 5,
            "tyre_life": [1, 2, 3, 4, 5],
            "lap_time_seconds": [90.1, 90.2, 90.3, 90.4, 90.5],
            "is_accurate": [True] * 5,
        }
    )
    model = TyreDegradationModel().fit(laps)
    assert model.fits["MEDIUM"].degradation_seconds_per_lap == pytest.approx(0.1, abs=0.02)
    assert model.predict("MEDIUM", 6) == pytest.approx(90.6, abs=0.05)


def test_model_rejects_data_without_enough_valid_laps() -> None:
    laps = pd.DataFrame(
        {"compound": ["SOFT"], "tyre_life": [1], "lap_time_seconds": [90.0]}
    )
    with pytest.raises(ValueError, match="At least two"):
        TyreDegradationModel().fit(laps)


def test_model_does_not_clamp_negative_wear_coefficients() -> None:
    laps = pd.DataFrame(
        {
            "compound": ["HARD"] * 5,
            "tyre_life": [1, 2, 3, 4, 5],
            "lap_number": [10, 11, 12, 13, 14],
            "lap_time_seconds": [91.0, 90.9, 90.8, 90.7, 90.6],
            "is_accurate": [True] * 5,
        }
    )
    model = TyreDegradationModel().fit(laps)
    assert model.fits["HARD"].degradation_seconds_per_lap < 0
