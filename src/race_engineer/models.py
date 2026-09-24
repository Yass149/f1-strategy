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

