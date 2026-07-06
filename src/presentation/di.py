from functools import lru_cache
from typing import Iterator

from fastapi import Depends
from sqlalchemy.orm import Session

from src.application.dispatcher import CommandDispatcher
from src.application.list_command import ListCommand
from src.application.release_command import ReleaseCommand
from src.application.take_command import TakeCommand
from src.domain.policy import StandResolutionPolicy
from src.infrastructure.config import Settings
from src.infrastructure.db import get_engine, get_session_factory
from src.infrastructure.repository import SqlAlchemyStandRepository


@lru_cache
def get_settings() -> Settings:
    return Settings()


def get_db_session(settings: Settings = Depends(get_settings)) -> Iterator[Session]:
    engine = get_engine(settings.database_url)
    session_factory = get_session_factory(engine)
    with session_factory() as session:
        yield session


def get_repository(session: Session = Depends(get_db_session)) -> SqlAlchemyStandRepository:
    return SqlAlchemyStandRepository(session)


def get_dispatcher(repository: SqlAlchemyStandRepository = Depends(get_repository)) -> CommandDispatcher:
    resolution_policy = StandResolutionPolicy()
    return CommandDispatcher(
        {
            "--list": ListCommand(repository),
            "--take": TakeCommand(repository, resolution_policy),
            "--free": ReleaseCommand(repository, resolution_policy),
        }
    )
