from fastapi import FastAPI, Request
import os
import httpx
import json
from app.firebase_client import db
from app.services.whatsapp_service import send_welcome_template, send_text

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
        elif user_input == "students":
            await handle_students(phone)

    except Exception as e:
        print("Parsing error:", e)

    return {"status": "ok"}

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

    chief = school_doc.get("Chief", "")
    name = school_doc.get("Name", "School")

    message = f"""
Hello Sir/Madam {chief},

Welcome to School Command Center of {name}.

Choose Action:
"""

    payload = {
        "phone": phone,
        "message": message,
        "buttons": [
            {"id": "students", "title": "Students"},
            {"id": "attendance", "title": "Attendance"},
            {"id": "fees", "title": "Fees"},
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
        data = doc.to_dict()
        data["id"] = doc.id   # add document id
        return data

    return None

def get_user_school(phone):

    doc = db.collection("railwayusers").document(phone).get()

    if doc.exists:
        return doc.to_dict().get("school_id")

    return None

async def handle_students(phone):

    school_id = get_user_school(phone)

    if not school_id:
        await send_text(phone, "Session expired. Please type *Principal* again.")
        return

    students_ref = db.collection("School").document(school_id).collection("Students")

    result = students_ref.count().get()

    count = result[0].value

    await send_text(phone, f"📊 Total Students: {count}")