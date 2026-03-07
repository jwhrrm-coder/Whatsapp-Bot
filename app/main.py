from fastapi import FastAPI, Request
import os
import httpx
import json
from app.firebase_client import db
from services.whatsapp_service import send_welcome_template, send_text

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
            user_input = message["text"]["body"].lower()

        elif msg_type == "button":
            user_input = message["button"]["payload"].lower()

        # MAIN BOT LOGIC
        if user_input in ["start", "hi", "hello"]:
            await send_welcome_template(phone)

        elif user_input == "new here":
            await send_text(phone, "👋 Welcome new user!")

        elif user_input == "parent":
            await send_text(phone, "👨‍👩‍👧 Parent services info.")

        elif user_input == "principal":
            await handle_principal(phone)

    except Exception as e:
        print("Parsing error:", e)

    return {"status": "ok"}

async def handle_principal(phone):

    cleaned = clean_phone(phone)

    school = get_school_by_phone(cleaned)

    if not school:
        await send_text(phone, "School not registered.")
        return

    chief = school.get("Chief", "Sir/Madam")
    name = school.get("Name", "School")

    message = f"""
Hello Sir/Madam {chief}, from {name}.

Welcome to School Command Center.

Choose Action:
"""

    payload = {
        "phone": phone,
        "message": message,
        "buttons": [
            {"id": "students", "title": "Students"},
            {"id": "attendance", "title": "Attendance"},
            {"id": "fees", "title": "Fees"},
            {"id": "reports", "title": "Reports"}
        ]
    }

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        await client.post(f"{BASE_URL}/api/send", json=payload, headers=headers)

def get_school_by_phone(phone):

    docs = db.collection("School").where("Phone", "==", phone).limit(1).stream()

    for doc in docs:
        return doc.to_dict()

    return None