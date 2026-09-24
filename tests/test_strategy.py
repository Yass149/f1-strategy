from race_engineer.models import StrategyRequest
from race_engineer.strategy import recommend_strategy


def test_strategy_recommends_pit_when_projected_degradation_exceeds_pit_loss() -> None:
    request = StrategyRequest(
        current_lap=40,
        total_laps=57,
        tyre_age=100,
        pit_loss_seconds=22,
        degradation_seconds_per_lap=0.08,
    )
    recommendation = recommend_strategy(request)
    assert recommendation.pit_now is True
    assert recommendation.projected_loss_if_staying_out == 136.0


def test_strategy_explains_when_staying_out_is_cheaper() -> None:
    request = StrategyRequest(
        current_lap=10,
        total_laps=57,
        tyre_age=1,
        pit_loss_seconds=22,
        degradation_seconds_per_lap=0.08,
    )
    recommendation = recommend_strategy(request)
    assert recommendation.pit_now is False
    assert "below" in recommendation.explanation

