from collections.abc import AsyncIterator
from functools import lru_cache
from typing import Annotated

from fastapi import Depends, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dispatcher import CommandDispatcher
from src.application.list_command import ListCommand
from src.application.release_command import ReleaseCommand
from src.application.take_command import TakeCommand
from src.domain.policy import StandResolutionPolicy
from src.infrastructure.channels import ChannelsRegistry
from src.infrastructure.config import Settings
from src.infrastructure.db import get_engine, get_session_factory
from src.infrastructure.repository import SqlAlchemyStandRepository
from src.presentation.schemas import MattermostWebhookRequest


@lru_cache
def get_settings() -> Settings:
    return Settings()


@lru_cache
def get_channels_registry() -> ChannelsRegistry:
    return ChannelsRegistry.from_config(get_settings().channels_config_path)


async def get_webhook_payload(
    payload: Annotated[MattermostWebhookRequest, Form()],
) -> MattermostWebhookRequest:
    return payload


def get_current_team(
    payload: MattermostWebhookRequest = Depends(get_webhook_payload),
    registry: ChannelsRegistry = Depends(get_channels_registry),
) -> str:
    team = registry.team_for_token(payload.token)
    if team is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return team


async def get_db_session(settings: Settings = Depends(get_settings)) -> AsyncIterator[AsyncSession]:
    engine = get_engine(settings.database_url)
    session_factory = get_session_factory(engine)
    async with session_factory() as session:
        yield session


def get_repository(
    team: str = Depends(get_current_team),
    session: AsyncSession = Depends(get_db_session),
) -> SqlAlchemyStandRepository:
    return SqlAlchemyStandRepository(session, team)


def get_dispatcher(repository: SqlAlchemyStandRepository = Depends(get_repository)) -> CommandDispatcher:
    resolution_policy = StandResolutionPolicy()
    return CommandDispatcher(
        {
            "--list": ListCommand(repository),
            "--take": TakeCommand(repository, resolution_policy),
            "--free": ReleaseCommand(repository, resolution_policy),
        }
    )
