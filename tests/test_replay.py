from race_engineer.replay import ReplayLap, replay_laps


def test_replay_returns_one_decision_per_observed_lap() -> None:
    decisions = replay_laps(
        [
            ReplayLap(lap_number=20, tyre_age=10, lap_time_seconds=90.0),
            ReplayLap(lap_number=21, tyre_age=11, lap_time_seconds=90.2),
        ],
        total_laps=57,
    )
    assert len(decisions) == 2
    assert decisions[0].lap_number == 20
    assert decisions[0].recommendation in {"PIT NOW", "STAY OUT"}

