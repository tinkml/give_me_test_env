from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.infrastructure.apm import configure_apm
from src.infrastructure.config import Settings
from src.infrastructure.db import get_engine, get_session_factory
from src.infrastructure.logger import configure_logging
from src.infrastructure.metrics import configure_metrics
from src.infrastructure.repository import SqlAlchemyStandRepository
from src.infrastructure.seeding import ensure_seeded
from src.infrastructure.sentry import configure_sentry
from src.presentation.exception_handlers import register_exception_handlers
from src.presentation.health import router as health_router
from src.presentation.routes import router


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved_settings = settings or Settings()
    configure_logging(resolved_settings.environment)
    configure_sentry(resolved_settings)
    engine = get_engine(resolved_settings.database_url)
    session_factory = get_session_factory(engine)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        async with session_factory() as session:
            await ensure_seeded(SqlAlchemyStandRepository(session), resolved_settings.stand_name_list)
        yield
        await engine.dispose()

    app = FastAPI(lifespan=lifespan)
    register_exception_handlers(app)
    configure_apm(app, resolved_settings)
    configure_metrics(app)
    app.include_router(router)
    app.include_router(health_router)
    return app


app = create_app()
