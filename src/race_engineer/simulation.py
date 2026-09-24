"""Counterfactual race-strategy simulation."""

from dataclasses import dataclass


@dataclass(frozen=True)
class StrategyComparison:
    stay_out_seconds: float
    pit_now_seconds: float
    pit_now_advantage_seconds: float
    recommendation: str
    decision_strength: str


@dataclass(frozen=True)
class StrategyWindow:
    pit_in_laps: int
    fresh_compound: str
    total_seconds: float
    advantage_seconds: float
    legal: bool


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
        decision_strength="MARGINAL" if abs(advantage) < 2.0 else "CLEAR",
    )


def compare_pit_windows(
    *,
    laps_remaining: int,
    current_tyre_age: int,
    current_compound: str,
    current_pace_seconds: float,
    current_degradation_seconds_per_lap: float,
    pit_loss_seconds: float,
    available_compounds: tuple[str, ...] = ("SOFT", "MEDIUM", "HARD"),
    dry_race: bool = True,
    max_wait_laps: int = 8,
) -> StrategyWindow:
    """Search legal pit windows and enforce two compounds in a dry race."""
    candidates: list[StrategyWindow] = []
    for wait in range(max(0, max_wait_laps) + 1):
        if wait >= laps_remaining:
            continue
        for compound in available_compounds:
            if dry_race and compound == current_compound:
                continue
            stay = sum(
                current_pace_seconds
                + (current_tyre_age + lap) * current_degradation_seconds_per_lap
                for lap in range(wait)
            )
            remaining = laps_remaining - wait
            pit = pit_loss_seconds + sum(
                current_pace_seconds - 1.0 + lap * 0.04 for lap in range(remaining)
            )
            total = stay + pit
            stay_out = sum(
                current_pace_seconds
                + (current_tyre_age + lap) * current_degradation_seconds_per_lap
                for lap in range(laps_remaining)
            )
            candidates.append(StrategyWindow(wait, compound, round(total, 3), round(stay_out - total, 3), True))
    if not candidates:
        return StrategyWindow(0, current_compound, 0.0, 0.0, False)
    return max(candidates, key=lambda candidate: candidate.advantage_seconds)
