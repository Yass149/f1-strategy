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

