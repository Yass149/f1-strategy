"""Time-aware strategy backtesting over processed lap features."""

from __future__ import annotations

import pandas as pd

from .simulation import compare_pit_now


def backtest_strategy(
    laps: pd.DataFrame,
    *,
    pit_loss_seconds: float = 22.0,
    degradation_seconds_per_lap: float = 0.08,
) -> dict:
    """Evaluate decisions using only information available at each lap.

    This is a decision replay, not a claim that the simulated counterfactual
    happened on track. It reports the recommendation distribution and the
    model's cumulative estimated advantage over the observed laps.
    """
    required = {"driver", "lap_number", "tyre_life", "lap_time_seconds"}
    missing = required.difference(laps.columns)
    if missing:
        raise ValueError(f"Lap features are missing required columns: {sorted(missing)}")
    clean = laps.dropna(subset=list(required)).copy()
    if "is_accurate" in clean:
        clean = clean[clean["is_accurate"].fillna(False).astype(bool)]
    total_laps = int(clean["lap_number"].max())
    decisions = []
    for row in clean.sort_values(["driver", "lap_number"]).itertuples(index=False):
        comparison = compare_pit_now(
            laps_remaining=max(total_laps - int(row.lap_number), 0),
            current_tyre_age=int(row.tyre_life),
            current_pace_seconds=float(row.lap_time_seconds),
            current_degradation_seconds_per_lap=degradation_seconds_per_lap,
            pit_loss_seconds=pit_loss_seconds,
        )
        decisions.append(comparison)
    if not decisions:
        raise ValueError("No accurate laps are available for backtesting")
    advantages = [decision.pit_now_advantage_seconds for decision in decisions]
    recommendations = [decision.recommendation for decision in decisions]
    return {
        "lap_count": len(decisions),
        "drivers": int(clean["driver"].nunique()),
        "pit_now_recommendations": recommendations.count("PIT NOW"),
        "stay_out_recommendations": recommendations.count("STAY OUT"),
        "marginal_decisions": sum(decision.decision_strength == "MARGINAL" for decision in decisions),
        "mean_pit_now_advantage_seconds": round(sum(advantages) / len(advantages), 3),
        "max_pit_now_advantage_seconds": round(max(advantages), 3),
        "min_pit_now_advantage_seconds": round(min(advantages), 3),
    }

