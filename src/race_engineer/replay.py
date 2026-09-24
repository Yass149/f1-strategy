"""Lap-by-lap strategy replay helpers."""

from pydantic import BaseModel, Field

from .simulation import compare_pit_now


class ReplayLap(BaseModel):
    lap_number: int = Field(ge=1)
    tyre_age: int = Field(ge=0)
    lap_time_seconds: float = Field(gt=0)


class ReplayDecision(BaseModel):
    lap_number: int
    recommendation: str
    pit_now_advantage_seconds: float


def replay_laps(
    laps: list[ReplayLap],
    total_laps: int,
    pit_loss_seconds: float = 22.0,
    degradation_seconds_per_lap: float = 0.08,
) -> list[ReplayDecision]:
    if not laps:
        return []
    return [
        ReplayDecision(
            lap_number=lap.lap_number,
            recommendation=(comparison := compare_pit_now(
                laps_remaining=max(total_laps - lap.lap_number, 0),
                current_tyre_age=lap.tyre_age,
                current_pace_seconds=lap.lap_time_seconds,
                current_degradation_seconds_per_lap=degradation_seconds_per_lap,
                pit_loss_seconds=pit_loss_seconds,
            )).recommendation,
            pit_now_advantage_seconds=comparison.pit_now_advantage_seconds,
        )
        for lap in laps
    ]

