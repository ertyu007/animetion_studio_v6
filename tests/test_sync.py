import pytest

from lib.sync import allocate_beats, make_schedule


def test_allocate_beats_preserves_total() -> None:
    values = allocate_beats([1, 2, 1], 8.0, minimum=0.5)
    assert sum(values) == pytest.approx(8.0)
    assert values[1] > values[0]


def test_tight_budget_scales_by_weight() -> None:
    values = allocate_beats([1, 2], 0.3, minimum=0.5)
    assert values == pytest.approx((0.1, 0.2))


def test_schedule_matches_audio_duration() -> None:
    schedule = make_schedule([1, 1, 2], 7.42)
    assert schedule.total == pytest.approx(7.42)


def test_schedule_without_cleanup_uses_no_exit() -> None:
    schedule = make_schedule([1], 2.0, has_cleanup=False)
    assert schedule.exit == 0
    assert schedule.total == pytest.approx(2.0)


def test_invalid_weights_fail() -> None:
    with pytest.raises(ValueError):
        allocate_beats([1, 0], 2.0)
