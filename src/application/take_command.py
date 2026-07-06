from datetime import datetime, timezone

from src.application.interfaces import StandRepository, StandPolicy
from src.domain.exceptions import StandNotFoundError


class TakeCommand:
    def __init__(self, repository: StandRepository, resolution_policy: StandPolicy) -> None:
        self._repository = repository
        self._resolution_policy = resolution_policy

    def execute(self, user_name: str, argument: str) -> str:
        stands = self._repository.list_all()

        try:
            stand = self._resolution_policy.resolve(argument, stands)
        except StandNotFoundError as error:
            return str(error)

        taken_stand = stand.take(user_name, datetime.now(timezone.utc))
        self._repository.save(taken_stand)
        return f"🤖 Пользователь {user_name} занял {taken_stand.name} "
