from src.application.interfaces import StandPolicy, StandRepository
from src.domain.exceptions import StandNotFoundError


class ReleaseCommand:
    def __init__(self, repository: StandRepository, policy: StandPolicy) -> None:
        self._repository = repository
        self._policy = policy

    async def execute(self, user_name: str, argument: str) -> str:
        stands = await self._repository.list_all()

        try:
            stand = self._policy.resolve(argument, stands)
        except StandNotFoundError as error:
            return str(error)

        released = stand.release()
        await self._repository.save(released)
        return f"🥳 {released.name} освобождён"
