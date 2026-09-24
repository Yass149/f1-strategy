import pandas as pd

from race_engineer.race_backtest import evaluate_future_laps


def test_future_evaluation_never_scores_training_laps() -> None:
    rows = []
    for lap in range(1, 9):
        rows.append({"driver": "VER", "team": "Red Bull", "compound": "MEDIUM", "lap_number": lap, "tyre_life": lap, "lap_time_seconds": 90 + lap * 0.1, "is_accurate": True})
    report = evaluate_future_laps(pd.DataFrame(rows), cutoff_lap=4)
    assert report["train_laps"] == 4
    assert report["test_laps"] == 4
    assert "model_mae_seconds" in report



def test_future_evaluation_skips_drivers_without_a_pre_cutoff_anchor() -> None:
    rows = []
    for lap in range(1, 9):
        rows.append({"driver": "VER", "team": "Red Bull", "compound": "MEDIUM", "lap_number": lap, "tyre_life": lap, "lap_time_seconds": 90 + lap * 0.1, "is_accurate": True})
    for lap in range(5, 9):
        rows.append({"driver": "HAM", "team": "Mercedes", "compound": "MEDIUM", "lap_number": lap, "tyre_life": lap, "lap_time_seconds": 91 + lap * 0.1, "is_accurate": True})
    report = evaluate_future_laps(pd.DataFrame(rows), cutoff_lap=4)
    assert report["test_laps"] == 4


def test_calibration_alpha_is_bounded_and_uses_known_laps() -> None:
    rows = []
    for lap in range(1, 13):
        rows.append({"driver": "VER", "team": "Red Bull", "compound": "MEDIUM", "lap_number": lap, "tyre_life": lap, "lap_time_seconds": 90 + lap * 0.1, "is_accurate": True})
    report = evaluate_future_laps(pd.DataFrame(rows), cutoff_lap=6)
    assert 0.0 <= report["calibration_alpha"] <= 1.0
