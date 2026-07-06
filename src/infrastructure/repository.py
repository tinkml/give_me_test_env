from sqlalchemy import select
from sqlalchemy.orm import Session

from src.infrastructure.utils import to_domain
from src.domain.stand import Stand
from src.infrastructure.models import StandModel


class SqlAlchemyStandRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_all(self) -> list[Stand]:
        statement = select(StandModel).order_by(StandModel.id)
        rows = self._session.execute(statement).scalars().all()
        return [to_domain(row) for row in rows]

    def get_by_name(self, name: str) -> Stand | None:
        statement = select(StandModel).where(StandModel.name == name)
        if row := self._session.execute(statement).scalar_one_or_none():
            return to_domain(row)
        return None

    def save(self, stand: Stand) -> None:
        statement = select(StandModel).where(StandModel.name == stand.name)
        row = self._session.execute(statement).scalar_one_or_none()

        if not row:
            row = StandModel(name=stand.name)
            self._session.add(row)

        row.status = stand.status
        row.occupied_by = stand.occupied_by
        row.occupied_since = stand.occupied_since
        self._session.commit()
