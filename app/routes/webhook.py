from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse
from app.config import VERIFY_TOKEN
from app.utils.parser import parse_message
from app.services.bot_service import handle_message

router = APIRouter()

@router.get("/webhook")
async def verify_webhook(
        hub_mode: str,
        hub_verify_token: str,
        hub_challenge: str
):
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return PlainTextResponse(hub_challenge)
    return "Verification failed"


@router.post("/webhook")
async def receive_message(request: Request):

    data = await request.json()

    phone, message = parse_message(data)

    if phone and message:
        await handle_message(phone, message)

    return {"status": "ok"}