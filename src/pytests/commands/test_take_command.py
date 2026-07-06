from src.application.take_command import TakeCommand
from src.domain.policy import StandResolutionPolicy
from src.domain.stand import Stand
from src.pytests.commands.fakes import FakeStandRepository


def test_take_marks_free_stand_occupied_by_caller() -> None:
    repository = FakeStandRepository([Stand(name="slplay7", status="free")])
    command = TakeCommand(repository, StandResolutionPolicy())

    result = command.execute(user_name="alice", argument="slplay7")

    assert "slplay7" in result
    assert "alice" in result
    saved = repository.get_by_name("slplay7")
    assert saved is not None
    assert saved.status == "occupied"
    assert saved.occupied_by == "alice"


def test_take_overwrites_existing_owner_without_check() -> None:
    repository = FakeStandRepository(
        [Stand(name="slplay7", status="occupied", occupied_by="alice")]
    )
    command = TakeCommand(repository, StandResolutionPolicy())

    command.execute(user_name="bob", argument="slplay7")

    saved = repository.get_by_name("slplay7")
    assert saved is not None
    assert saved.occupied_by == "bob"


def test_take_unknown_stand_returns_error_message_without_state_change() -> None:
    repository = FakeStandRepository([Stand(name="slplay7", status="free")])
    command = TakeCommand(repository, StandResolutionPolicy())

    result = command.execute(user_name="alice", argument="unknown")

    assert "не найден" in result
    saved = repository.get_by_name("slplay7")
    assert saved is not None
    assert saved.status == "free"
