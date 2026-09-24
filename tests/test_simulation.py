import pytest

from race_engineer.simulation import compare_pit_now


def test_pit_now_wins_when_old_tyres_are_slow() -> None:
    result = compare_pit_now(
        laps_remaining=20,
        current_tyre_age=30,
        current_pace_seconds=90,
        current_degradation_seconds_per_lap=0.2,
        pit_loss_seconds=20,
    )
    assert result.recommendation == "PIT NOW"
    assert result.pit_now_advantage_seconds > 0


def test_staying_out_wins_when_pit_loss_is_too_high() -> None:
    result = compare_pit_now(
        laps_remaining=2,
        current_tyre_age=1,
        current_pace_seconds=90,
        current_degradation_seconds_per_lap=0.01,
        pit_loss_seconds=30,
    )
    assert result.recommendation == "STAY OUT"
    assert result.pit_now_advantage_seconds < 0


def test_simulator_rejects_negative_laps() -> None:
    with pytest.raises(ValueError, match="laps_remaining"):
        compare_pit_now(
            laps_remaining=-1,
            current_tyre_age=1,
            current_pace_seconds=90,
            current_degradation_seconds_per_lap=0.1,
            pit_loss_seconds=20,
        )

