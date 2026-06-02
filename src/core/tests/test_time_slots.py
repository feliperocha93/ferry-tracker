from datetime import UTC, datetime

from core.utils.time_slots import SAO_PAULO, current_collection_slot


def test_slot_truncates_to_hour_when_before_half() -> None:
    at = datetime(2026, 5, 30, 10, 15, 45, tzinfo=SAO_PAULO)
    slot = current_collection_slot(at)
    assert slot == datetime(2026, 5, 30, 13, 0, tzinfo=UTC)


def test_slot_truncates_to_half_when_after_half() -> None:
    at = datetime(2026, 5, 30, 10, 45, 0, tzinfo=SAO_PAULO)
    slot = current_collection_slot(at)
    assert slot == datetime(2026, 5, 30, 13, 30, tzinfo=UTC)


def test_slot_exactly_on_half_hour() -> None:
    at = datetime(2026, 5, 30, 10, 30, 0, tzinfo=SAO_PAULO)
    slot = current_collection_slot(at)
    assert slot == datetime(2026, 5, 30, 13, 30, tzinfo=UTC)


def test_slot_exactly_on_hour() -> None:
    at = datetime(2026, 5, 30, 10, 0, 0, tzinfo=SAO_PAULO)
    slot = current_collection_slot(at)
    assert slot == datetime(2026, 5, 30, 13, 0, tzinfo=UTC)


def test_naive_datetime_treated_as_sao_paulo() -> None:
    at = datetime(2026, 5, 30, 10, 15)
    slot = current_collection_slot(at)
    assert slot.tzinfo == UTC
