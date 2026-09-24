"""HTTP API for the first Race Engineer vertical slice."""

from fastapi import FastAPI

from .frontend import dashboard
from .models import (
    ReplayDecision,
    ReplayRequest,
    StrategyComparisonRequest,
    StrategyRecommendation,
    StrategyRequest,
)
from .replay import replay_laps
from .simulation import StrategyComparison, compare_pit_now
from .strategy import recommend_strategy

app = FastAPI(title="Race Engineer AI", version="0.1.0")


@app.get("/", include_in_schema=False)
def home():
    return dashboard()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/strategy/recommend", response_model=StrategyRecommendation)
def strategy_recommend(request: StrategyRequest) -> StrategyRecommendation:
    return recommend_strategy(request)


@app.post("/strategy/compare", response_model=StrategyComparison)
def strategy_compare(request: StrategyComparisonRequest) -> StrategyComparison:
    return compare_pit_now(**request.model_dump())


@app.post("/strategy/replay", response_model=list[ReplayDecision])
def strategy_replay(request: ReplayRequest) -> list[ReplayDecision]:
    return replay_laps(
        request.laps,
        total_laps=request.total_laps,
        pit_loss_seconds=request.pit_loss_seconds,
        degradation_seconds_per_lap=request.degradation_seconds_per_lap,
    )
