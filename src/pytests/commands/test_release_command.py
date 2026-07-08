from src.application.release_command import ReleaseCommand
from src.domain.policy import StandResolutionPolicy
from src.domain.stand import Stand
from src.pytests.commands.fakes import FakeStandRepository


async def test_release_frees_occupied_stand() -> None:
    repository = FakeStandRepository(
        [Stand(name="slplay7", status="occupied", occupied_by="alice")]
    )
    command = ReleaseCommand(repository, StandResolutionPolicy())

    result = await command.execute(user_name="bob", argument="slplay7")

    assert "slplay7" in result
    saved = await repository.get_by_name("slplay7")
    assert saved is not None
    assert saved.status == "free"
    assert saved.occupied_by is None


async def test_release_does_not_check_caller_is_owner() -> None:
    repository = FakeStandRepository(
        [Stand(name="slplay7", status="occupied", occupied_by="alice")]
    )
    command = ReleaseCommand(repository, StandResolutionPolicy())

    result = await command.execute(user_name="bob", argument="slplay7")

    assert "не найден" not in result


async def test_release_unknown_stand_returns_error_message() -> None:
    command = ReleaseCommand(FakeStandRepository([]), StandResolutionPolicy())

    result = await command.execute(user_name="bob", argument="unknown")

    assert "не найден" in result
