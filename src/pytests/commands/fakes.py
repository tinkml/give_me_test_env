from src.domain.stand import Stand


class FakeStandRepository:
    def __init__(self, stands: list[Stand] | None = None) -> None:
        self._stands: dict[str, Stand] = {stand.name: stand for stand in (stands or [])}

    def list_all(self) -> list[Stand]:
        return list(self._stands.values())

    def get_by_name(self, name: str) -> Stand | None:
        return self._stands.get(name)

    def save(self, stand: Stand) -> None:
        self._stands[stand.name] = stand
