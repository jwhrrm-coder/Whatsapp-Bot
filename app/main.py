from fastapi import FastAPI, Request
import os
import httpx

app = FastAPI()

API_TOKEN = os.getenv("WHATSAPP_API_KEY")
BASE_URL = "https://live.theautomate.ai"


@app.get("/")
def home():
    return {"status": "bot running"}


@app.post("/webhook")
async def webhook(request: Request):

    data = await request.json()
    print("Webhook data:", data)

    # Example extraction (depends on AutomateAI payload)
    phone = data.get("from")

    if phone:
        await send_whatsapp_message(phone)

    return {"status": "ok"}


async def send_whatsapp_message(phone: str):

    payload = {
        "phone": phone,
        "message": "Hello John, how are you?",
        "header": "Test header",
        "footer": "Test footer",
        "buttons": [
            {"id": "id_1", "title": "Fine"},
            {"id": "id_2", "title": "Not well"}
        ]
    }

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        await client.post(
            f"{BASE_URL}/api/send",
            json=payload,
            headers=headers
        )