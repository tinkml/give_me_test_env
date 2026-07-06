import pytest

from src.domain.policy import StandNotFoundError, StandResolutionPolicy
from src.domain.stand import Stand

STANDS = [
    Stand(name="akb1", status="free"),
    Stand(name="slplay4", status="free"),
    Stand(name="slplay7", status="free"),
]


def test_resolve_by_exact_name() -> None:
    policy = StandResolutionPolicy()

    resolved = policy.resolve("slplay7", STANDS)

    assert resolved.name == "slplay7"


def test_resolve_by_one_based_index() -> None:
    policy = StandResolutionPolicy()

    resolved = policy.resolve("2", STANDS)

    assert resolved.name == "slplay4"


def test_resolve_unknown_name_raises() -> None:
    policy = StandResolutionPolicy()

    with pytest.raises(StandNotFoundError) as exc_info:
        policy.resolve("unknown", STANDS)

    assert exc_info.value.identifier == "unknown"


def test_resolve_index_zero_raises() -> None:
    policy = StandResolutionPolicy()

    with pytest.raises(StandNotFoundError):
        policy.resolve("0", STANDS)


def test_resolve_index_out_of_range_raises() -> None:
    policy = StandResolutionPolicy()

    with pytest.raises(StandNotFoundError):
        policy.resolve("99", STANDS)
