from src.application.interfaces import StandRepository

from src.application.formatters import StandsMarkdownFormatter


class ListCommand:
    def __init__(self, repository: StandRepository) -> None:
        self._repository = repository

    async def execute(self, user_name: str, argument: str) -> str:
        stands = await self._repository.list_all()
        return StandsMarkdownFormatter.format(stands)
