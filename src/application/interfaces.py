from typing import Protocol

from src.domain.stand import Stand


class StandRepository(Protocol):
    async def list_all(self) -> list[Stand]: ...

    async def get_by_name(self, name: str) -> Stand | None: ...

    async def save(self, stand: Stand) -> None: ...


class StandPolicy(Protocol):

    def resolve(self, identifier: str, stands: list[Stand]) -> Stand:...


class Command(Protocol):
    async def execute(self, user_name: str, argument: str) -> str: ...

class ResponseBuilder(Protocol):
    def build(self, stand: Stand) -> Stand: ...