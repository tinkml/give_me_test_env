from datetime import datetime, timezone

from src.application.list_command import ListCommand
from src.domain.stand import Stand
from src.pytests.commands.fakes import FakeStandRepository


def test_list_formats_free_and_occupied_stands() -> None:
    when = datetime(2026, 7, 5, 12, 0, tzinfo=timezone.utc)
    repository = FakeStandRepository(
        [
            Stand(name="akb1", status="free"),
            Stand(name="slplay4", status="occupied", occupied_by="alice", occupied_since=when),
        ]
    )
    command = ListCommand(repository)

    result = command.execute(user_name="bob", argument="")

    assert result == (
        "1. akb1 — Свободен\n"
        "2. slplay4 — Занят alice с 2026-07-05 12:00"
    )


def test_list_on_empty_repository_returns_empty_string() -> None:
    command = ListCommand(FakeStandRepository([]))

    assert command.execute(user_name="bob", argument="") == ""
