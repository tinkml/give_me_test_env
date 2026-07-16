from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException

from src.application.dispatcher import CommandDispatcher
from src.infrastructure.config import Settings
from src.infrastructure.logger import logger
from src.presentation.di import get_dispatcher, get_settings
from src.presentation.schemas import MattermostWebhookRequest, OutgoingWebhookResponse

router = APIRouter()


@router.post("/webhook", response_model=OutgoingWebhookResponse)
async def handle_webhook(
    payload: Annotated[MattermostWebhookRequest, Form()],
    settings: Settings = Depends(get_settings),
    dispatcher: CommandDispatcher = Depends(get_dispatcher),
) -> OutgoingWebhookResponse:

    if payload.token != settings.stands_bot_webhook_token:
        raise HTTPException(status_code=401, detail="Invalid token")

    logger.info("webhook_received", trigger_word=payload.trigger_word, user_name=payload.user_name)

    argument = payload.text[len(payload.trigger_word) :].strip()
    response_text = await dispatcher.dispatch(payload.trigger_word, payload.user_name, argument)

    logger.info("command_dispatched", trigger_word=payload.trigger_word, user_name=payload.user_name)

    return OutgoingWebhookResponse(text=response_text)
