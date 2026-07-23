import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.db import get_engine, get_session_factory
from src.infrastructure.models import Base, StandModel


@pytest.fixture
async def session() -> AsyncSession:
    engine = get_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    session_factory = get_session_factory(engine)
    async with session_factory() as db_session:
        yield db_session


async def test_team_defaults_to_no_team_when_omitted(session: AsyncSession) -> None:
    session.add(StandModel(name="akb1", status="free"))
    await session.commit()

    row = (await session.execute(select(StandModel).where(StandModel.name == "akb1"))).scalar_one()

    assert row.team == "no_team"


async def test_team_accepts_explicit_value(session: AsyncSession) -> None:
    session.add(StandModel(name="dev-1", status="free", team="sl"))
    await session.commit()

    row = (await session.execute(select(StandModel).where(StandModel.name == "dev-1"))).scalar_one()

    assert row.team == "sl"


def test_team_column_is_indexed() -> None:
    indexed_columns = {column.name for index in StandModel.__table__.indexes for column in index.columns}

    assert "team" in indexed_columns
