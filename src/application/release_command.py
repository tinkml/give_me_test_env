from src.application.interfaces import StandRepository, StandPolicy
from src.domain.exceptions import StandNotFoundError


class ReleaseCommand:
    def __init__(self, repository: StandRepository, policy: StandPolicy) -> None:
        self._repository = repository
        self._policy = policy

    def execute(self, user_name: str, argument: str) -> str:
        stands = self._repository.list_all()

        try:
            stand = self._policy.resolve(argument, stands)
        except StandNotFoundError as error:
            return str(error)

        released = stand.release()
        self._repository.save(released)
        return f"🥳 {released.name} освобождён"
