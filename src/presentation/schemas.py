from typing import Annotated

from fastapi import Form
from pydantic import BaseModel


class OutgoingWebhookResponse(BaseModel):
    text: str


class MattermostWebhookRequest(BaseModel):
    token: Annotated[str, Form(...)]
    channel_id: Annotated[str, Form(...)]
    user_name: Annotated[str, Form(...)]
    text: Annotated[str, Form(...)]
    trigger_word: Annotated[str, Form(...)]
