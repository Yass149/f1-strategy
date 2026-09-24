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
    lap_number_coefficient: float = 0.0
    driver_terms: dict[str, float] | None = None
    team_terms: dict[str, float] | None = None


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
        return _predict_fit(fit, tyre_life, 0.0, None, None)

    def predict_with_context(
        self,
        compound: str,
        tyre_life: float,
        lap_number: float,
        driver: str | None = None,
        team: str | None = None,
    ) -> float:
        if self.global_fit is None:
            raise RuntimeError("Fit the model before predicting")
        return _predict_fit(
            self.fits.get(compound, self.global_fit), tyre_life, lap_number, driver, team
        )

    def to_dict(self) -> dict:
        return {
            "global": _fit_to_dict(self.global_fit),
            "compounds": {key: _fit_to_dict(value) for key, value in self.fits.items()},
        }


def _fit_line(laps: pd.DataFrame) -> CompoundFit:
    working = laps.copy()
    for column, default in (("lap_number", 0), ("driver", "UNKNOWN"), ("team", "UNKNOWN")):
        if column not in working:
            working[column] = default
    matrix = pd.DataFrame({"tyre_life": working["tyre_life"].astype(float), "lap_number": working["lap_number"].astype(float)})
    driver = pd.get_dummies(working["driver"].astype(str), prefix="driver", drop_first=True, dtype=float)
    team = pd.get_dummies(working["team"].astype(str), prefix="team", drop_first=True, dtype=float)
    matrix = pd.concat([matrix, driver, team], axis=1)
    design = np.column_stack([np.ones(len(matrix)), matrix.to_numpy(dtype=float)])
    # Fuel proxy and tyre age are correlated during a stint. A small ridge
    # penalty keeps the driver/team terms stable without clipping wear rates.
    penalty = np.eye(design.shape[1]) * 1.0
    penalty[0, 0] = 0.0
    response = working["lap_time_seconds"].astype(float).to_numpy()
    augmented_design = np.vstack([design, np.sqrt(penalty)])
    augmented_response = np.concatenate([response, np.zeros(design.shape[1])])
    coefficients, *_ = np.linalg.lstsq(augmented_design, augmented_response, rcond=None)
    names = ["intercept", *matrix.columns.tolist()]
    coefficient_map = dict(zip(names, coefficients))
    return CompoundFit(
        baseline_seconds=round(float(coefficient_map["intercept"]), 4),
        degradation_seconds_per_lap=round(float(coefficient_map.get("tyre_life", 0.0)), 4),
        sample_count=len(working),
        lap_number_coefficient=round(float(coefficient_map.get("lap_number", 0.0)), 4),
        driver_terms={key: round(float(value), 4) for key, value in coefficient_map.items() if key.startswith("driver_")},
        team_terms={key: round(float(value), 4) for key, value in coefficient_map.items() if key.startswith("team_")},
    )


def _predict_fit(
    fit: CompoundFit,
    tyre_life: float,
    lap_number: float,
    driver: str | None,
    team: str | None,
) -> float:
    value = fit.baseline_seconds + fit.degradation_seconds_per_lap * tyre_life
    value += fit.lap_number_coefficient * lap_number
    if driver and fit.driver_terms:
        value += fit.driver_terms.get(f"driver_{driver}", 0.0)
    if team and fit.team_terms:
        value += fit.team_terms.get(f"team_{team}", 0.0)
    return value


def _fit_to_dict(fit: CompoundFit | None) -> dict | None:
    if fit is None:
        return None
    return {
        "baseline_seconds": fit.baseline_seconds,
        "degradation_seconds_per_lap": fit.degradation_seconds_per_lap,
        "sample_count": fit.sample_count,
        "lap_number_coefficient": fit.lap_number_coefficient,
        "driver_terms": fit.driver_terms or {},
        "team_terms": fit.team_terms or {},
    }
