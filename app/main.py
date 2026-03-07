from fastapi import FastAPI, Request
import os
import httpx
import json

app = FastAPI()

TOKEN = os.getenv("WHATSAPP_API_KEY")
BASE_URL = "https://live.theautomate.ai"


@app.get("/")
def home():
    return {"status": "bot running"}


@app.post("/webhook")
async def webhook(request: Request):

    payload = await request.json()
    print(json.dumps(payload, indent=2))

    # ignore events that are not user messages
    if payload.get("event") != "message.received":
        return {"status": "ignored"}

    try:
        message = payload["data"]["data"]["value"]["messages"][0]

        phone = message["from"]
        if not phone.startswith("+"):
            phone = "+" + phone

        msg_type = message["type"]

        # TEXT
        if msg_type == "text":
            text = message["text"]["body"].lower()

            if text == "start":
                await send_welcome_template(phone)

        # BUTTON CLICK
        elif msg_type == "button":

            button = message["button"]["payload"]

            if button == "New Here":
                await send_text(phone, "👋 Welcome new user!")

            elif button == "Parent":
                await send_text(phone, "👨‍👩‍👧 Parent services info.")

            elif button == "Principal":
                await send_text(phone, "🏫 Principal dashboard info.")

    except Exception as e:
        print("Parsing error:", e)

    return {"status": "ok"}

async def send_welcome_template(phone):

    payload = {
        "phone": phone,
        "template": {
            "name": "welcome",
            "language": {
                "code": "en"
            }
        }
    }

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/send/template",
            json=payload,
            headers=headers
        )

    print("Template response:", response.text)


async def send_text(phone, text):

    payload = {
        "phone": phone,
        "message": text
    }

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/send",
            json=payload,
            headers=headers
        )

    print("Text response:", response.text)