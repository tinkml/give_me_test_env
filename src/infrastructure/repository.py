from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.stand import Stand
from src.infrastructure.models import StandModel
from src.infrastructure.utils import to_domain


class SqlAlchemyStandRepository:
    def __init__(self, session: AsyncSession, team: str) -> None:
        self._session = session
        self._team = team

    async def list_all(self) -> list[Stand]:
        statement = select(StandModel).where(StandModel.team == self._team).order_by(StandModel.id)
        result = await self._session.execute(statement)
        rows = result.scalars().all()
        return [to_domain(row) for row in rows]

    async def get_by_name(self, name: str) -> Stand | None:
        statement = select(StandModel).where(StandModel.name == name, StandModel.team == self._team)
        result = await self._session.execute(statement)
        if row := result.scalar_one_or_none():
            return to_domain(row)
        return None

    async def save(self, stand: Stand) -> None:
        statement = select(StandModel).where(StandModel.name == stand.name, StandModel.team == self._team)
        result = await self._session.execute(statement)
        row = result.scalar_one_or_none()

        if not row:
            row = StandModel(name=stand.name, team=self._team)
            self._session.add(row)

        row.status = stand.status
        row.occupied_by = stand.occupied_by
        row.occupied_since = stand.occupied_since
        await self._session.commit()
