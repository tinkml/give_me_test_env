from src.application.interfaces import StandRepository
from src.domain.stand import Stand


def ensure_seeded(repository: StandRepository, stand_names: list[str]) -> None:
    existing_names = {stand.name for stand in repository.list_all()}
    for name in stand_names:
        if name not in existing_names:
            repository.save(Stand(name=name, status="free"))
