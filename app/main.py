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

    try:
        message = payload["data"]["data"]["value"]["messages"][0]

        phone = message["from"]
        text = message["text"]["body"].lower()

        if text == "start":
            await send_welcome_template(phone)

        else:
            await send_text(phone, "Type *start* to begin.")

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
        await client.post(
            f"{BASE_URL}/api/send",
            json=payload,
            headers=headers
        )
