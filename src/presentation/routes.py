import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException

from src.presentation.di import get_dispatcher, get_settings
from src.presentation.schemas import MattermostWebhookRequest, OutgoingWebhookResponse
from src.application.dispatcher import CommandDispatcher
from src.infrastructure.config import Settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/webhook", response_model=OutgoingWebhookResponse)
async def handle_webhook(
    payload: Annotated[MattermostWebhookRequest, Form()],
    settings: Settings = Depends(get_settings),
    dispatcher: CommandDispatcher = Depends(get_dispatcher),
) -> OutgoingWebhookResponse:

    if payload.token != settings.stands_bot_webhook_token:
        raise HTTPException(status_code=401, detail="Invalid token")

    argument = payload.text[len(payload.trigger_word):].strip()
    try:
        response_text = await dispatcher.dispatch(payload.trigger_word, payload.user_name, argument)
    except Exception:
        logger.exception("Command execution failed for trigger_word=%s", payload.trigger_word)
        return OutgoingWebhookResponse(text="Внутренняя ошибка, попробуйте позже")

    return OutgoingWebhookResponse(text=response_text)
