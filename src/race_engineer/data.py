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


def _timedelta_seconds(values: pd.Series) -> pd.Series:
    if pd.api.types.is_timedelta64_dtype(values):
        return values.dt.total_seconds()
    return pd.to_numeric(values, errors="coerce")
