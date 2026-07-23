import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.stand import Stand
from src.infrastructure.db import get_engine, get_session_factory
from src.infrastructure.models import Base, StandModel
from src.infrastructure.repository import SqlAlchemyStandRepository


@pytest.fixture
async def session() -> AsyncSession:
    engine = get_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    session_factory = get_session_factory(engine)
    async with session_factory() as db_session:
        yield db_session


async def test_save_and_get_by_name_round_trip(session: AsyncSession) -> None:
    repository = SqlAlchemyStandRepository(session, team="akb")
    await repository.save(Stand(name="akb1", status="free"))

    result = await repository.get_by_name("akb1")

    assert result is not None
    assert result.name == "akb1"
    assert result.status == "free"


async def test_get_by_name_returns_none_when_missing(session: AsyncSession) -> None:
    repository = SqlAlchemyStandRepository(session, team="akb")

    assert await repository.get_by_name("missing") is None


async def test_save_updates_existing_row_by_name(session: AsyncSession) -> None:
    repository = SqlAlchemyStandRepository(session, team="akb")
    await repository.save(Stand(name="akb1", status="free"))

    await repository.save(Stand(name="akb1", status="occupied", occupied_by="alice"))

    result = await repository.get_by_name("akb1")
    assert result is not None
    assert result.status == "occupied"
    assert result.occupied_by == "alice"


async def test_list_all_preserves_insertion_order(session: AsyncSession) -> None:
    repository = SqlAlchemyStandRepository(session, team="akb")
    await repository.save(Stand(name="akb1", status="free"))
    await repository.save(Stand(name="slplay4", status="free"))

    result = await repository.list_all()

    assert [stand.name for stand in result] == ["akb1", "slplay4"]


async def test_save_stamps_team_on_new_stand(session: AsyncSession) -> None:
    repository = SqlAlchemyStandRepository(session, team="sl")
    await repository.save(Stand(name="dev-1", status="free"))

    row = (await session.execute(select(StandModel).where(StandModel.name == "dev-1"))).scalar_one()
    assert row.team == "sl"


async def test_list_all_only_returns_stands_of_its_own_team(session: AsyncSession) -> None:
    akb_repository = SqlAlchemyStandRepository(session, team="akb")
    sl_repository = SqlAlchemyStandRepository(session, team="sl")
    await akb_repository.save(Stand(name="akb1", status="free"))
    await sl_repository.save(Stand(name="dev-1", status="free"))

    assert [stand.name for stand in await akb_repository.list_all()] == ["akb1"]
    assert [stand.name for stand in await sl_repository.list_all()] == ["dev-1"]


async def test_get_by_name_does_not_leak_across_teams(session: AsyncSession) -> None:
    akb_repository = SqlAlchemyStandRepository(session, team="akb")
    sl_repository = SqlAlchemyStandRepository(session, team="sl")
    await akb_repository.save(Stand(name="akb1", status="free"))

    assert await akb_repository.get_by_name("akb1") is not None
    assert await sl_repository.get_by_name("akb1") is None
