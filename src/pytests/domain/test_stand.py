from datetime import datetime, timezone

from src.domain.stand import Stand


def test_new_stand_is_free_by_default() -> None:
    stand = Stand(name="slplay7", status="free")

    assert stand.status == "free"
    assert stand.occupied_by is None
    assert stand.occupied_since is None


def test_take_marks_stand_occupied() -> None:
    stand = Stand(name="slplay7", status="free")
    when = datetime(2026, 7, 5, 12, 0, tzinfo=timezone.utc)

    taken = stand.take("alice", when)

    assert taken.status == "occupied"
    assert taken.occupied_by == "alice"
    assert taken.occupied_since == when


def test_take_is_unconditional_and_overwrites_current_owner() -> None:
    when = datetime(2026, 7, 5, 12, 0, tzinfo=timezone.utc)
    stand = Stand(name="slplay7", status="occupied", occupied_by="alice", occupied_since=when)

    taken = stand.take("bob", when)

    assert taken.occupied_by == "bob"


def test_release_clears_occupancy() -> None:
    when = datetime(2026, 7, 5, 12, 0, tzinfo=timezone.utc)
    stand = Stand(name="slplay7", status="occupied", occupied_by="alice", occupied_since=when)

    released = stand.release()

    assert released.status == "free"
    assert released.occupied_by is None
    assert released.occupied_since is None


def test_stand_is_immutable() -> None:
    stand = Stand(name="slplay7", status="free")

    assert stand.take("alice", datetime.now(timezone.utc)) is not stand
