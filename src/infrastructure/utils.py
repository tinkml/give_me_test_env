from src.domain.stand import Stand
from src.infrastructure.models import StandModel


def to_domain(db_model: StandModel) -> Stand:
    return Stand(
        name=db_model.name,
        status=db_model.status,
        occupied_by=db_model.occupied_by,
        occupied_since=db_model.occupied_since,
    )
