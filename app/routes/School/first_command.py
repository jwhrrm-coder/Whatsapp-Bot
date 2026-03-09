import os

import httpx

from app.firebase_client import db
from app.main import clean_phone
from app.routes.School.helper import get_school_by_phone
from app.services.whatsapp_service import send_text

TOKEN = os.getenv("WHATSAPP_API_KEY")
BASE_URL = "https://live.theautomate.ai"

async def handle_principal(phone):

    cleaned = clean_phone(phone)

    school_doc = get_school_by_phone(cleaned)

    if not school_doc:
        await send_text(phone, "School not registered.")
        return

    school_id = school_doc["id"]

    # SAVE SESSION
    db.collection("railwayusers").document(phone).set({
        "school_id": school_id,
        "role": "principal"
    }, merge=True)

    chief = school_doc.get("Chief", "Principal")
    name = school_doc.get("Name", "School")

    message = f"""
Welcome to {name} 🎓

Dear {chief},
Thank you for connecting with us. We are pleased to have {name} with our system.

Our team is here to provide quick support for all services related to your school's students and administrative activities.

Please choose an action below:
"""

    payload = {
        "phone": phone,
        "message": message,
        "buttons": [
            {"id": "attendance", "title": "Attendance"},
            {"id": "fees", "title": "Fees"},
            {"id": "other", "title": "Other"},
        ]
    }

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        await client.post(f"{BASE_URL}/api/send", json=payload, headers=headers)


async def handle_other_menu(phone):

    message = "Choose additional action:"

    payload = {
        "phone": phone,
        "message": message,
        "buttons": [
            {"id": "announcement", "title": "Announcement"},
            {"id": "idcard", "title": "IDCard"},
            {"id": "start", "title": "Start"},
        ]
    }

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        await client.post(f"{BASE_URL}/api/send", json=payload, headers=headers)
