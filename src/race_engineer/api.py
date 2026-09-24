"""HTTP API for the first Race Engineer vertical slice."""

from fastapi import FastAPI

from .models import StrategyComparisonRequest, StrategyRecommendation, StrategyRequest
from .simulation import StrategyComparison, compare_pit_now
from .strategy import recommend_strategy

app = FastAPI(title="Race Engineer AI", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/strategy/recommend", response_model=StrategyRecommendation)
def strategy_recommend(request: StrategyRequest) -> StrategyRecommendation:
    return recommend_strategy(request)


@app.post("/strategy/compare", response_model=StrategyComparison)
def strategy_compare(request: StrategyComparisonRequest) -> StrategyComparison:
    return compare_pit_now(**request.model_dump())
