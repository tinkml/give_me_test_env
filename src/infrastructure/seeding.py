from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces import StandRepository
from src.domain.stand import Stand
from src.infrastructure.channels import ChannelsRegistry
from src.infrastructure.models import StandModel


async def ensure_seeded(repository: StandRepository, stand_names: list[str]) -> None:
    existing_names = {stand.name for stand in await repository.list_all()}
    for name in stand_names:
        if name not in existing_names:
            await repository.save(Stand(name=name, status="free"))


async def reassign_teams(session: AsyncSession, registry: ChannelsRegistry) -> None:
    for team in registry.teams():
        stands = registry.stands_for_team(team)
        statement = (
            update(StandModel).where(StandModel.name.in_(stands), StandModel.team != team).values(team=team)
        )
        await session.execute(statement)
    await session.commit()
