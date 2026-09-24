"""Small domain models used by the first vertical slice."""

from pydantic import BaseModel, Field


class StrategyRequest(BaseModel):
    current_lap: int = Field(ge=1)
    total_laps: int = Field(gt=1)
    tyre_age: int = Field(ge=0)
    pit_loss_seconds: float = Field(default=22.0, gt=0)
    degradation_seconds_per_lap: float = Field(default=0.08, ge=0)


class StrategyRecommendation(BaseModel):
    pit_now: bool
    projected_loss_if_staying_out: float
    pit_window: tuple[int, int]
    explanation: str


class StrategyComparisonRequest(BaseModel):
    laps_remaining: int = Field(ge=0)
    current_tyre_age: int = Field(ge=0)
    current_pace_seconds: float = Field(gt=0)
    current_degradation_seconds_per_lap: float = Field(ge=0)
    pit_loss_seconds: float = Field(gt=0)
    fresh_tyre_pace_delta_seconds: float = -1.0
    fresh_tyre_degradation_seconds_per_lap: float = Field(default=0.04, ge=0)


class ReplayLap(BaseModel):
    lap_number: int = Field(ge=1)
    tyre_age: int = Field(ge=0)
    lap_time_seconds: float = Field(gt=0)


class ReplayDecision(BaseModel):
    lap_number: int
    recommendation: str
    pit_now_advantage_seconds: float


class ReplayRequest(BaseModel):
    total_laps: int = Field(gt=1)
    laps: list[ReplayLap] = Field(min_length=1)
    pit_loss_seconds: float = Field(default=22.0, gt=0)
    degradation_seconds_per_lap: float = Field(default=0.08, ge=0)
