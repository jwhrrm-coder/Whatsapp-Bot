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

    data = await request.json()
    print(json.dumps(data, indent=2))

    phone = data.get("from")
    message = data.get("message", {}).get("text", "").lower()

    if not phone:
        return {"status": "ignored"}

    if message in ["hi", "hello", "start"]:
        await send_welcome(phone)

    elif message == "fine":
        await send_text(phone, "Glad you're doing well! 😊")

    elif message == "not well":
        await send_text(phone, "Hope things get better soon ❤️")

    else:
        await send_text(phone, "Type *hi* to start.")

    return {"status": "ok"}


async def send_welcome(phone):

    payload = {
        "phone": phone,
        "message": "Hello! How are you today?",
        "header": "Welcome",
        "footer": "Choose an option",
        "buttons": [
            {"id": "fine", "title": "Fine"},
            {"id": "not_well", "title": "Not well"}
        ]
    }

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        await client.post(f"{BASE_URL}/api/send", json=payload, headers=headers)

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
        await client.post(f"{BASE_URL}/api/send", json=payload, headers=headers)

