"""Historical race-data ingestion and leakage-safe lap features.

FastF1 is an optional dependency. Keeping the import inside ``load_session``
means the API and unit tests remain usable before data is downloaded.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Union

import pandas as pd


def load_session(
    year: int,
    event: Union[str, int],
    session_name: str = "R",
    cache_dir: Union[str, Path] = "data/cache/fastf1",
) -> Any:
    """Load and cache a FastF1 session.

    ``event`` can be a round number or an event name such as ``"Monza"``.
    The returned object is the native FastF1 ``Session`` so downstream work
    can access laps, telemetry, weather, and messages when needed.
    """

    try:
        import fastf1
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError(
            "FastF1 is optional. Install it with `pip install -e '.[data]'`."
        ) from exc

    cache_path = Path(cache_dir)
    cache_path.mkdir(parents=True, exist_ok=True)
    fastf1.Cache.enable_cache(str(cache_path))
    session = fastf1.get_session(year, event, session_name)
    session.load(telemetry=False, weather=False, messages=False)
    return session


def build_lap_features(laps: pd.DataFrame) -> pd.DataFrame:
    """Create a compact lap table suitable for time-aware modelling.

    The output only contains information known by the end of each lap. The
    next-lap target is intentionally omitted until the evaluation design is
    finalised, preventing accidental use of future information in features.
    """

    required = {"Driver", "LapNumber", "LapTime"}
    missing = required.difference(laps.columns)
    if missing:
        raise ValueError(f"Lap table is missing required columns: {sorted(missing)}")

    output = pd.DataFrame(index=laps.index)
    output["driver"] = laps["Driver"].astype("string")
    output["lap_number"] = pd.to_numeric(laps["LapNumber"], errors="coerce")
    output["lap_time_seconds"] = _timedelta_seconds(laps["LapTime"])

    for source, target in (
        ("Compound", "compound"),
        ("TyreLife", "tyre_life"),
        ("Stint", "stint"),
        ("Team", "team"),
        ("IsAccurate", "is_accurate"),
    ):
        if source in laps:
            output[target] = laps[source].values

    output = output.sort_values(["driver", "lap_number"])
    return output.reset_index(drop=True)


def summarise_lap_file(path: Union[str, Path]) -> dict:
    """Return a small, dashboard-safe summary of a processed lap file."""
    file_path = Path(path)
    if not file_path.exists():
        return {"available": False, "path": str(file_path)}
    laps = pd.read_parquet(file_path, columns=["driver", "lap_number"])
    return {
        "available": True,
        "path": str(file_path),
        "lap_count": len(laps),
        "driver_count": int(laps["driver"].nunique()),
        "drivers": sorted(laps["driver"].dropna().astype(str).unique().tolist()),
        "lap_min": int(laps["lap_number"].min()),
        "lap_max": int(laps["lap_number"].max()),
    }


def read_lap_sample(path: Union[str, Path], driver: str = "VER", limit: int = 60) -> list[dict]:
    """Read a bounded driver lap sample for the dashboard."""
    file_path = Path(path)
    if not file_path.exists():
        return []
    laps = pd.read_parquet(file_path)
    if "is_accurate" in laps:
        laps = laps[laps["is_accurate"].fillna(False).astype(bool)]
    selected = laps[laps["driver"].astype(str).eq(driver)].head(max(1, min(limit, 200)))
    columns = [column for column in ["driver", "lap_number", "lap_time_seconds", "tyre_life", "compound"] if column in selected]
    return selected[columns].where(selected[columns].notna(), None).to_dict(orient="records")


def read_driver_context(path: Union[str, Path], driver: str) -> dict:
    """Return the latest accurate lap as strategy-form defaults."""
    file_path = Path(path)
    if not file_path.exists():
        return {"available": False}
    laps = pd.read_parquet(file_path)
    accurate = laps[laps["is_accurate"].fillna(False).astype(bool)]
    driver_laps = accurate[accurate["driver"].astype(str).eq(driver)].sort_values("lap_number")
    if driver_laps.empty:
        return {"available": False, "driver": driver}
    latest = driver_laps.iloc[-1]
    total_laps = int(laps["lap_number"].max())
    return {
        "available": True,
        "driver": driver,
        "current_lap": int(latest["lap_number"]),
        "laps_remaining": max(total_laps - int(latest["lap_number"]), 0),
        "tyre_age": int(latest["tyre_life"]),
        "current_pace_seconds": float(latest["lap_time_seconds"]),
        "compound": str(latest["compound"]),
    }


def _timedelta_seconds(values: pd.Series) -> pd.Series:
    if pd.api.types.is_timedelta64_dtype(values):
        return values.dt.total_seconds()
    return pd.to_numeric(values, errors="coerce")
