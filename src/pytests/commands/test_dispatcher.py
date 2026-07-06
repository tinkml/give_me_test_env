import pytest

from src.application.dispatcher import CommandDispatcher, UnknownTriggerWordError


class _StubCommand:
    def __init__(self, response: str) -> None:
        self._response = response
        self.calls: list[tuple[str, str]] = []

    def execute(self, user_name: str, argument: str) -> str:
        self.calls.append((user_name, argument))
        return self._response


def test_dispatch_routes_to_matching_command() -> None:
    list_command = _StubCommand("stands list")
    dispatcher = CommandDispatcher({"!list": list_command})

    result = dispatcher.dispatch("!list", user_name="alice", argument="")

    assert result == "stands list"
    assert list_command.calls == [("alice", "")]


def test_dispatch_unknown_trigger_word_raises() -> None:
    dispatcher = CommandDispatcher({"!list": _StubCommand("x")})

    with pytest.raises(UnknownTriggerWordError):
        dispatcher.dispatch("!unknown", user_name="alice", argument="")
