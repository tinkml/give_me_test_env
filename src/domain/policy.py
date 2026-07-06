import contextlib

from src.domain.exceptions import StandNotFoundError
from src.domain.stand import Stand


class StandResolutionPolicy:

    @classmethod
    def resolve(cls, identifier: str, stands: list[Stand]) -> Stand:
        identifier = identifier.strip()

        with contextlib.suppress(ValueError):
            # Пробуем получить стэнд по индексу
            index = int(identifier) - 1
            if index < 0 or index >= len(stands):
                raise StandNotFoundError(identifier)
            return stands[index]

        # Пробуем получить стэнд по названию
        for stand in stands:
            if stand.name == identifier:
                return stand

        raise StandNotFoundError(identifier)
