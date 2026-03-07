import os
import httpx

TOKEN = os.getenv("WHATSAPP_API_KEY")
BASE_URL = "https://live.theautomate.ai"


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