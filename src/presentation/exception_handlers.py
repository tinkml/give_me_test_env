import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.application.dispatcher import UnknownTriggerWordError
from src.domain.exceptions import StandNotFoundError
from src.infrastructure.logger import logger
from src.presentation.schemas import OutgoingWebhookResponse

WEBHOOK_PATH = "/webhook"


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(StandNotFoundError, _handle_stand_not_found)  # noqa
    app.add_exception_handler(UnknownTriggerWordError, _handle_unknown_trigger_word)  # noqa
    app.add_exception_handler(Exception, _handle_unexpected_error)


async def _handle_stand_not_found(request: Request, exc: StandNotFoundError) -> JSONResponse:
    logger.warning("stand_not_found", path=request.url.path, identifier=exc.identifier)
    return JSONResponse(OutgoingWebhookResponse(text=str(exc)).model_dump())


async def _handle_unknown_trigger_word(request: Request, exc: UnknownTriggerWordError) -> JSONResponse:
    logger.warning("unknown_trigger_word", path=request.url.path, trigger_word=exc.trigger_word)
    return JSONResponse(OutgoingWebhookResponse(text=str(exc)).model_dump())


async def _handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("unhandled_exception", path=request.url.path)
    sentry_sdk.capture_exception(exc)
    return JSONResponse(OutgoingWebhookResponse(text="Внутренняя ошибка, попробуйте позже").model_dump())
