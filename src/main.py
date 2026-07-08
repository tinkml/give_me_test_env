from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from src.presentation.routes import router
from src.infrastructure.config import Settings
from src.infrastructure.db import get_engine, get_session_factory
from src.infrastructure.repository import SqlAlchemyStandRepository
from src.infrastructure.seeding import ensure_seeded


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved_settings = settings or Settings()
    engine = get_engine(resolved_settings.database_url)
    session_factory = get_session_factory(engine)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        async with session_factory() as session:
            await ensure_seeded(SqlAlchemyStandRepository(session), resolved_settings.stand_name_list)
        yield
        await engine.dispose()

    app = FastAPI(lifespan=lifespan)
    app.include_router(router)
    return app


app = create_app()
