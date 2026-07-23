import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.stand import Stand
from src.infrastructure.channels import ChannelConfig, ChannelsRegistry
from src.infrastructure.db import get_engine, get_session_factory
from src.infrastructure.models import Base, StandModel
from src.infrastructure.repository import SqlAlchemyStandRepository
from src.infrastructure.seeding import ensure_seeded, reassign_teams
from src.pytests.commands.fakes import FakeStandRepository


@pytest.fixture
async def session() -> AsyncSession:
    engine = get_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    session_factory = get_session_factory(engine)
    async with session_factory() as db_session:
        yield db_session


async def test_ensure_seeded_adds_missing_stands_as_free() -> None:
    repository = FakeStandRepository([])

    await ensure_seeded(repository, ["akb1", "slplay4"])

    names = {stand.name for stand in await repository.list_all()}
    assert names == {"akb1", "slplay4"}
    assert all(stand.status == "free" for stand in await repository.list_all())


async def test_ensure_seeded_does_not_touch_existing_stand() -> None:
    repository = FakeStandRepository([Stand(name="akb1", status="occupied", occupied_by="alice")])

    await ensure_seeded(repository, ["akb1"])

    saved = await repository.get_by_name("akb1")
    assert saved is not None
    assert saved.status == "occupied"
    assert saved.occupied_by == "alice"


async def test_ensure_seeded_does_not_delete_stands_missing_from_list() -> None:
    repository = FakeStandRepository([Stand(name="legacy", status="free")])

    await ensure_seeded(repository, ["akb1"])

    names = {stand.name for stand in await repository.list_all()}
    assert "legacy" in names
    assert "akb1" in names


async def test_reassign_teams_retags_existing_stand_to_its_configured_team(session: AsyncSession) -> None:
    session.add(StandModel(name="akb1", status="free", team="no_team"))
    await session.commit()
    registry = ChannelsRegistry.build(
        [ChannelConfig(team="akb", token_env="WEBHOOK_TOKEN_AKB", stands=["akb1"])],
        {"WEBHOOK_TOKEN_AKB": "akb-secret"},
    )

    await reassign_teams(session, registry)

    row = (await session.execute(select(StandModel).where(StandModel.name == "akb1"))).scalar_one()
    assert row.team == "akb"


async def test_reassign_teams_preserves_status_of_retagged_stand(session: AsyncSession) -> None:
    session.add(StandModel(name="akb1", status="occupied", occupied_by="alice", team="no_team"))
    await session.commit()
    registry = ChannelsRegistry.build(
        [ChannelConfig(team="akb", token_env="WEBHOOK_TOKEN_AKB", stands=["akb1"])],
        {"WEBHOOK_TOKEN_AKB": "akb-secret"},
    )

    await reassign_teams(session, registry)

    row = (await session.execute(select(StandModel).where(StandModel.name == "akb1"))).scalar_one()
    assert row.status == "occupied"
    assert row.occupied_by == "alice"


async def test_reassign_teams_does_not_touch_stands_already_on_the_right_team(session: AsyncSession) -> None:
    session.add(StandModel(name="dev-1", status="free", team="sl"))
    await session.commit()
    registry = ChannelsRegistry.build(
        [ChannelConfig(team="akb", token_env="WEBHOOK_TOKEN_AKB", stands=["akb1"])],
        {"WEBHOOK_TOKEN_AKB": "akb-secret"},
    )

    await reassign_teams(session, registry)

    row = (await session.execute(select(StandModel).where(StandModel.name == "dev-1"))).scalar_one()
    assert row.team == "sl"


async def test_per_team_seeding_creates_missing_stands_for_each_team(session: AsyncSession) -> None:
    registry = ChannelsRegistry.build(
        [
            ChannelConfig(team="akb", token_env="WEBHOOK_TOKEN_AKB", stands=["akb1"]),
            ChannelConfig(team="sl", token_env="WEBHOOK_TOKEN_SL", stands=["dev-1"]),
        ],
        {"WEBHOOK_TOKEN_AKB": "akb-secret", "WEBHOOK_TOKEN_SL": "sl-secret"},
    )

    for team in registry.teams():
        await ensure_seeded(SqlAlchemyStandRepository(session, team), registry.stands_for_team(team))

    akb_repository = SqlAlchemyStandRepository(session, "akb")
    sl_repository = SqlAlchemyStandRepository(session, "sl")
    assert [stand.name for stand in await akb_repository.list_all()] == ["akb1"]
    assert [stand.name for stand in await sl_repository.list_all()] == ["dev-1"]
