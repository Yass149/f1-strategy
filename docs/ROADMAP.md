# Race Engineer AI — model upgrade plan

The headline test is future-stint lap-time MAE on unseen races versus repeating the last observed lap. Every change is evaluated on the same holdout.

## Completed in this iteration

- Calibrated the learned tyre/fuel/driver/team movement against known laps only.
- Clamped the calibration weight to `[0, 1]`, making zero exactly equal to the last-lap baseline.
- Re-evaluated all 24 2024 races: model MAE **1.344s** versus baseline **1.498s**.
- The model improves 12 of 24 races; the full per-race report remains in the generated evaluation artifact.

## Next upgrades

1. Join timestamp-safe weather observations to each lap.
2. Add explicit track-state and compound-transition features.
3. Report error by compound, driver, race condition and cutoff lap.
4. Add a validated live-timing adapter separate from historical replay.

The model is still a research system. Weather, radio, live timing and race-control signals are not connected yet.
