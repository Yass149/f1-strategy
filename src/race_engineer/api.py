"""HTTP API for the first Race Engineer vertical slice."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Query

from .backtest import backtest_strategy
from .data import read_driver_context, read_lap_sample, summarise_lap_file
from .frontend import dashboard
from .models import (
    ReplayDecision,
    ReplayRequest,
    StrategyComparisonRequest,
    StrategyRecommendation,
    StrategyRequest,
    StrategyWindowRequest,
)
from .replay import replay_laps
from .simulation import StrategyComparison, StrategyWindow, compare_pit_now, compare_pit_windows
from .strategy import recommend_strategy

app = FastAPI(title="Race Engineer AI", version="0.1.0")
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "monza_2024_race.parquet"


@app.get("/", include_in_schema=False)
def home():
    return dashboard()


@app.get("/dashboard", include_in_schema=False)
def dashboard_page():
    return dashboard()


@app.get("/data/summary")
def data_summary():
    return summarise_lap_file(DATA_PATH)


@app.get("/data/laps")
def data_laps(driver: str = Query(default="VER", min_length=3, max_length=3), limit: int = Query(default=60, ge=1, le=200)):
    return read_lap_sample(DATA_PATH, driver, limit)


@app.get("/data/context")
def data_context(driver: str = Query(default="VER", min_length=3, max_length=3), lap: Optional[int] = Query(default=None, ge=1, le=100)):  # noqa: UP045
    return read_driver_context(DATA_PATH, driver, lap)


@app.get("/evaluation/backtest")
def evaluation_backtest():
    import pandas as pd

    path = DATA_PATH
    if not Path(path).exists():
        return {"available": False, "message": "Download a processed session before running the backtest."}
    return backtest_strategy(pd.read_parquet(path))


@app.get("/evaluation/season-headline")
def evaluation_season_headline():
    import json

    path = PROJECT_ROOT / "artifacts" / "season_2024_evaluation.json"
    if not path.exists():
        return {"available": False, "message": "Run scripts/evaluate_season.py to publish the season headline."}
    payload = json.loads(path.read_text())
    if isinstance(payload, dict):
        headline = payload.get("headline", {})
    else:
        model = [row.get("model_mae_seconds") for row in payload if row.get("model_mae_seconds") is not None]
        baseline = [row.get("last_lap_baseline_mae_seconds") for row in payload if row.get("last_lap_baseline_mae_seconds") is not None]
        headline = {
            "model_mae_seconds": sum(model) / len(model) if model else None,
            "baseline_mae_seconds": sum(baseline) / len(baseline) if baseline else None,
            "races": len(payload),
        }
    return {"available": True, **headline}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/strategy/recommend", response_model=StrategyRecommendation)
def strategy_recommend(request: StrategyRequest) -> StrategyRecommendation:
    return recommend_strategy(request)


@app.post("/strategy/compare", response_model=StrategyComparison)
def strategy_compare(request: StrategyComparisonRequest) -> StrategyComparison:
    return compare_pit_now(**request.model_dump())


@app.post("/strategy/windows", response_model=StrategyWindow)
def strategy_windows(request: StrategyWindowRequest) -> StrategyWindow:
    return compare_pit_windows(**request.model_dump())


@app.post("/strategy/replay", response_model=list[ReplayDecision])
def strategy_replay(request: ReplayRequest) -> list[ReplayDecision]:
    return replay_laps(
        request.laps,
        total_laps=request.total_laps,
        pit_loss_seconds=request.pit_loss_seconds,
        degradation_seconds_per_lap=request.degradation_seconds_per_lap,
    )
