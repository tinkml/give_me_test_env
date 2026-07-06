from src.presentation.schemas import OutgoingWebhookResponse


def test_response_serializes_text_field() -> None:
    response = OutgoingWebhookResponse(text="1. akb1 — Свободен")

    assert response.model_dump() == {"text": "1. akb1 — Свободен"}
