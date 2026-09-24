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
| Baseline minus model (improvement) | +0.154 s |

The model improves on the baseline in **11 of 24 races** at cutoff lap 20.
The same holdout at different decision times is: 

| Cutoff | Model MAE | Baseline MAE |
| ---: | ---: | ---: |
| Lap 20 | 1.344 s | 1.498 s |
| Lap 30 | 1.383 s | 1.564 s |
| Lap 40 | 1.103 s | 1.249 s |

Compound-level and stint-transition metrics are included in the generated JSON
report for each held-out race. The dashboard presents the model as an
explainable research system, not as an autonomous race-winning predictor.

The next modelling iteration needs circuit-relative pace, fuel-load proxies,
stint-level alignment, and weather/track-condition features before the model
should control a strategy recommendation automatically.
