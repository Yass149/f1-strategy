import pandas as pd

from race_engineer.backtest import backtest_strategy


def test_backtest_reports_decision_distribution() -> None:
    laps = pd.DataFrame(
        {
            "driver": ["VER", "VER", "HAM", "HAM"],
            "lap_number": [1, 2, 1, 2],
            "tyre_life": [1, 2, 1, 2],
            "lap_time_seconds": [90.0, 90.1, 91.0, 91.1],
            "is_accurate": [True, True, True, True],
        }
    )
    report = backtest_strategy(laps)
    assert report["lap_count"] == 4
    assert report["drivers"] == 2
    assert report["pit_now_recommendations"] + report["stay_out_recommendations"] == 4

