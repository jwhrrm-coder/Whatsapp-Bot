from fastapi import FastAPI, Request
import os
import httpx
import json
from app.firebase_client import db
from app.routes.School.first_command import handle_principal, handle_other_menu
from app.routes.School.second import handle_attendance, handle_finance
from app.services.whatsapp_service import send_welcome_template, send_text
from datetime import datetime
from zoneinfo import ZoneInfo

app = FastAPI()

TOKEN = os.getenv("WHATSAPP_API_KEY")
BASE_URL = "https://live.theautomate.ai"

@app.get("/")
def home():
    return {"status": "bot running"}

def clean_phone(phone: str):
    phone = phone.replace("+", "")
    if phone.startswith("91"):
        phone = phone[2:]
    return phone

@app.post("/webhook")
async def webhook(request: Request):

    payload = await request.json()
    print(json.dumps(payload, indent=2))

    if payload.get("event") != "message.received":
        return {"status": "ignored"}

    try:
        message = payload["data"]["data"]["value"]["messages"][0]

        phone = message["from"]
        if not phone.startswith("+"):
            phone = "+" + phone

        msg_type = message["type"]

        user_input = ""

        if msg_type == "text":
            user_input = message["text"]["body"].strip().lower()

        elif msg_type == "interactive":
            interactive = message.get("interactive", {})
            if interactive.get("type") == "button_reply":
                user_input = interactive["button_reply"]["id"].strip().lower()

        # MAIN BOT LOGIC
        if user_input in ["start", "hi", "hello"]:
            await send_welcome_template(phone)

        elif user_input == "new here" or user_input == "New here":
            await send_text(phone, "👋 Welcome new user!")

        elif user_input == "parent":
            await send_text(phone, "👨‍👩‍👧 Parent services info.")

        elif user_input == "principal" :
            await handle_principal(phone)
        elif user_input == "other":
            await handle_other_menu(phone)
        elif user_input == "attendance" :
            await handle_attendance(phone)
        elif user_input == "fees" :
            await handle_finance(phone)

    except Exception as e:
        print("Parsing error:", e)

    return {"status": "ok"}