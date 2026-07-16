from src.application.interfaces import Command


class UnknownTriggerWordError(Exception):
    def __init__(self, trigger_word: str) -> None:
        self.trigger_word = trigger_word
        msg = f"Неизвестное триггер-слово: {trigger_word}"
        super().__init__(msg)


class CommandDispatcher:
    def __init__(self, commands: dict[str, Command]) -> None:
        self._commands = commands

    async def dispatch(self, trigger_word: str, user_name: str, argument: str) -> str:
        command = self._commands.get(trigger_word)
        if not command:
            raise UnknownTriggerWordError(trigger_word)

        return await command.execute(user_name, argument)
