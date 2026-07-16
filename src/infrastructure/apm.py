from elasticapm import Client
from elasticapm.contrib.starlette import ElasticAPM
from fastapi import FastAPI

from src.infrastructure.config import Settings


def configure_apm(app: FastAPI, settings: Settings) -> None:
    if not settings.elastic_apm_server_url:
        return

    client = Client(
        {
            "SERVICE_NAME": settings.elastic_apm_service_name,
            "SERVER_URL": settings.elastic_apm_server_url,
            "ENVIRONMENT": settings.environment,
        }
    )
    app.add_middleware(ElasticAPM, client=client)
