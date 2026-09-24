# Evaluation protocol

The project now downloads and processes every 2024 race session with the same
lap-quality filters. The season evaluator holds out one race at a time, fits
on laps available by the cutoff plus the other races, and predicts only laps
after the cutoff. The prediction is anchored to each driver's last known lap
so circuit pace does not leak into the comparison.

The first complete run used cutoff lap 20 across all 24 races. The single
headline number is **1.344 seconds MAE** for future stint lap times on unseen
races, compared with **1.498 seconds MAE** for the last-lap baseline.

Detailed averages:

| Measure | Mean absolute error |
| --- | ---: |
| Air-temperature-aware calibrated fuel/tyre/driver/team model | 1.344 s |
| Last known lap baseline | 1.498 s |
| Model minus baseline | +1.417 s |

The model improves on the baseline in 2 of 24 races. This is a valid negative
result: the current features do not yet support a reliable cross-circuit pace
forecast. The dashboard therefore presents the model as an explainable
research baseline, not as a race-winning predictor.

The next modelling iteration needs circuit-relative pace, fuel-load proxies,
stint-level alignment, and weather/track-condition features before the model
should control a strategy recommendation automatically.
