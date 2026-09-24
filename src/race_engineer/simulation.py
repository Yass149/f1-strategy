"""Counterfactual race-strategy simulation."""

from dataclasses import dataclass


@dataclass(frozen=True)
class StrategyComparison:
    stay_out_seconds: float
    pit_now_seconds: float
    pit_now_advantage_seconds: float
    recommendation: str


def compare_pit_now(
    *,
    laps_remaining: int,
    current_tyre_age: int,
    current_pace_seconds: float,
    current_degradation_seconds_per_lap: float,
    pit_loss_seconds: float,
    fresh_tyre_pace_delta_seconds: float = -1.0,
    fresh_tyre_degradation_seconds_per_lap: float = 0.04,
) -> StrategyComparison:
    """Compare stay-out and pit-now outcomes over the remaining laps."""
    if laps_remaining < 0:
        raise ValueError("laps_remaining must be non-negative")
    if min(current_tyre_age, current_pace_seconds, pit_loss_seconds) < 0:
        raise ValueError("ages, pace, and pit loss cannot be negative")

    stay_out = sum(
        current_pace_seconds
        + (current_tyre_age + lap) * current_degradation_seconds_per_lap
        for lap in range(laps_remaining)
    )
    pit_now = pit_loss_seconds + sum(
        current_pace_seconds
        + fresh_tyre_pace_delta_seconds
        + lap * fresh_tyre_degradation_seconds_per_lap
        for lap in range(laps_remaining)
    )
    advantage = stay_out - pit_now
    return StrategyComparison(
        stay_out_seconds=round(stay_out, 3),
        pit_now_seconds=round(pit_now, 3),
        pit_now_advantage_seconds=round(advantage, 3),
        recommendation="PIT NOW" if advantage > 0 else "STAY OUT",
    )

