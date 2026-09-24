"""Leakage-safe future-stint evaluation against a last-lap baseline."""

from __future__ import annotations

import pandas as pd

from .degradation import TyreDegradationModel


def evaluate_future_laps(
    laps: pd.DataFrame, cutoff_lap: int = 20, training_laps: pd.DataFrame | None = None
) -> dict:
    """Fit on laps up to ``cutoff_lap`` and score later laps only."""
    required = {"driver", "team", "compound", "lap_number", "tyre_life", "lap_time_seconds"}
    missing = required.difference(laps.columns)
    if missing:
        raise ValueError(f"Lap features are missing required columns: {sorted(missing)}")
    clean = laps.dropna(subset=list(required)).copy()
    if "is_accurate" in clean:
        clean = clean[clean["is_accurate"].fillna(False).astype(bool)]
    known = clean[clean["lap_number"] <= cutoff_lap]
    train = known if training_laps is None else pd.concat([training_laps, known], ignore_index=True)
    if "is_accurate" in train:
        train = train[train["is_accurate"].fillna(False).astype(bool)]
    test = clean[clean["lap_number"] > cutoff_lap]
    anchors = known.sort_values(["driver", "lap_number"]).groupby("driver").last()
    # A driver who has no clean lap before the cutoff cannot be scored without
    # inventing a baseline context. Exclude those rows and report the scored set.
    test = test[test["driver"].isin(anchors.index)]
    if len(train) < 4 or test.empty:
        raise ValueError("Need at least four training laps and future laps with known anchors")
    model = TyreDegradationModel().fit(train)

    weather_columns = ("AirTemp",)

    def weather_context(row) -> dict[str, float]:
        return {column: float(getattr(row, column)) for column in weather_columns if hasattr(row, column) and pd.notna(getattr(row, column))}

    def model_delta(row, anchor):
        predicted = model.predict_with_context(str(row.compound), row.tyre_life, row.lap_number, str(row.driver), str(row.team), weather_context(row))
        anchor_weather = {column: float(anchor[column]) for column in weather_columns if column in anchor.index and pd.notna(anchor[column])}
        anchored = model.predict_with_context(str(anchor["compound"]), anchor["tyre_life"], anchor["lap_number"], str(row.driver), str(anchor["team"]), anchor_weather)
        return float(predicted - anchored)

    known_deltas = []
    known_errors = []
    for row in known.itertuples(index=False):
        anchor = anchors.loc[row.driver]
        if row.lap_number != anchor["lap_number"]:
            known_deltas.append(model_delta(row, anchor))
            known_errors.append(float(row.lap_time_seconds - anchor["lap_time_seconds"]))
    denominator = sum(value * value for value in known_deltas)
    alpha = sum(value * error for value, error in zip(known_deltas, known_errors)) / denominator if denominator else 0.0
    alpha = max(0.0, min(1.0, alpha))
    predictions = []
    actual = []
    for row in test.itertuples(index=False):
        anchor = anchors.loc[row.driver]
        base = float(anchor["lap_time_seconds"])
        predictions.append(base + alpha * model_delta(row, anchor))
        actual.append(float(row.lap_time_seconds))
    baseline = [float(anchors.loc[row.driver, "lap_time_seconds"]) for row in test.itertuples()]
    model_mae = sum(abs(prediction - truth) for prediction, truth in zip(predictions, actual)) / len(actual)
    baseline_mae = sum(abs(prediction - truth) for prediction, truth in zip(baseline, actual)) / len(actual)
    return {
        "cutoff_lap": cutoff_lap,
        "train_laps": len(train),
        "test_laps": len(test),
        "calibration_alpha": round(alpha, 4),
        "model_mae_seconds": round(model_mae, 4),
        "last_lap_baseline_mae_seconds": round(baseline_mae, 4),
        "improvement_seconds": round(baseline_mae - model_mae, 4),
    }
