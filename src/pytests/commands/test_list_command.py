from datetime import UTC, datetime

from src.application.list_command import ListCommand
from src.domain.stand import Stand
from src.pytests.commands.fakes import FakeStandRepository


async def test_list_formats_free_and_occupied_stands() -> None:
    when = datetime(2026, 7, 5, 12, 0, tzinfo=UTC)
    repository = FakeStandRepository(
        [
            Stand(name="akb1", status="free"),
            Stand(name="slplay4", status="occupied", occupied_by="alice", occupied_since=when),
        ]
    )
    command = ListCommand(repository)

    result = await command.execute(user_name="bob", argument="")

    assert result == (
        "| № | stand | status | user | since |\n"
        "|-|-|-|-|-|\n"
        "| 1 | akb1 | ✅ Свободен | | |\n"
        "| 2 | slplay4 | 🚫 Занят | alice | 2026-07-05 12:00 |"
    )


async def test_list_on_empty_repository_returns_header_only_table() -> None:
    command = ListCommand(FakeStandRepository([]))

    assert await command.execute(user_name="bob", argument="") == (
        "| № | stand | status | user | since |\n|-|-|-|-|-|"
    )
