from race_engineer.simulation import compare_pit_windows


def test_dry_race_search_uses_a_different_compound() -> None:
    result = compare_pit_windows(
        laps_remaining=20,
        current_tyre_age=18,
        current_compound="MEDIUM",
        current_pace_seconds=90,
        current_degradation_seconds_per_lap=0.1,
        pit_loss_seconds=22,
    )
    assert result.legal is True
    assert result.fresh_compound != "MEDIUM"

