"""Interpretable tyre-degradation estimation from lap stints."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class CompoundFit:
    """Linear pace estimate: lap time = baseline + degradation * tyre life."""

    baseline_seconds: float
    degradation_seconds_per_lap: float
    sample_count: int


class TyreDegradationModel:
    """Fit one robust, easy-to-explain pace line for each tyre compound."""

    def __init__(self) -> None:
        self.fits: dict[str, CompoundFit] = {}
        self.global_fit: CompoundFit | None = None

    def fit(self, laps: pd.DataFrame) -> TyreDegradationModel:
        required = {"compound", "tyre_life", "lap_time_seconds"}
        missing = required.difference(laps.columns)
        if missing:
            raise ValueError(f"Lap features are missing required columns: {sorted(missing)}")

        clean = laps.copy()
        if "is_accurate" in clean:
            clean = clean[clean["is_accurate"].fillna(False).astype(bool)]
        clean = clean.dropna(subset=["compound", "tyre_life", "lap_time_seconds"])
        clean = clean[(clean["tyre_life"] > 0) & (clean["lap_time_seconds"] > 0)]
        if len(clean) < 2:
            raise ValueError("At least two valid accurate laps are required")

        self.global_fit = _fit_line(clean)
        self.fits = {
            str(compound): _fit_line(group)
            for compound, group in clean.groupby("compound")
            if len(group) >= 2
        }
        return self

    def predict(self, compound: str, tyre_life: float) -> float:
        if self.global_fit is None:
            raise RuntimeError("Fit the model before predicting")
        fit = self.fits.get(compound, self.global_fit)
        return fit.baseline_seconds + fit.degradation_seconds_per_lap * tyre_life

    def to_dict(self) -> dict:
        return {
            "global": _fit_to_dict(self.global_fit),
            "compounds": {key: _fit_to_dict(value) for key, value in self.fits.items()},
        }


def _fit_line(laps: pd.DataFrame) -> CompoundFit:
    x = laps["tyre_life"].astype(float).to_numpy()
    y = laps["lap_time_seconds"].astype(float).to_numpy()
    slope, intercept = np.polyfit(x, y, 1)
    return CompoundFit(
        baseline_seconds=round(float(intercept), 4),
        degradation_seconds_per_lap=round(max(float(slope), 0.0), 4),
        sample_count=len(laps),
    )


def _fit_to_dict(fit: CompoundFit | None) -> dict | None:
    if fit is None:
        return None
    return {
        "baseline_seconds": fit.baseline_seconds,
        "degradation_seconds_per_lap": fit.degradation_seconds_per_lap,
        "sample_count": fit.sample_count,
    }
