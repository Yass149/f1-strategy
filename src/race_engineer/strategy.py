"""Transparent baseline strategy logic.

This is deliberately a baseline, not the final ML model. It gives us a
testable decision surface before introducing historical data and learning.
"""

from .models import StrategyRecommendation, StrategyRequest


def recommend_strategy(request: StrategyRequest) -> StrategyRecommendation:
    laps_remaining = request.total_laps - request.current_lap
    projected_loss = request.tyre_age * request.degradation_seconds_per_lap * max(laps_remaining, 0)
    pit_now = projected_loss > request.pit_loss_seconds
    start = max(request.current_lap, request.total_laps - 20)
    end = min(request.total_laps - 1, request.current_lap + 8)
    if pit_now:
        explanation = (
            f"Tyre degradation projects {projected_loss:.1f}s over {laps_remaining} laps, "
            f"above the {request.pit_loss_seconds:.1f}s pit-lane cost."
        )
    else:
        explanation = (
            f"Staying out projects {projected_loss:.1f}s of tyre loss, below the "
            f"{request.pit_loss_seconds:.1f}s pit-lane cost."
        )
    return StrategyRecommendation(
        pit_now=pit_now,
        projected_loss_if_staying_out=round(projected_loss, 2),
        pit_window=(start, end),
        explanation=explanation,
    )

