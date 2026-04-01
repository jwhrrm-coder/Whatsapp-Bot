from fastapi import FastAPI, Request
import os
import httpx
import json
from app.firebase_client import db
from app.routes.Parents.helper.handle_selection import handle_meetings, handle_notices, handle_parent_fees, handle_parent_selection, handle_present_status, handle_warnings, handle_warnings, show_parent_other_menu
from app.routes.Parents.parent_handler import handle_parent
from app.routes.School.first_command import handle_principal, handle_other_menu
from app.routes.School.second import handle_attendance, handle_finance, handle_idcard_status
from app.routes.admin.admin import handle_admin
from app.routes.admin.superadmin import handle_admin_warnings, handle_all_orders, handle_all_schools,handle_superadmin
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
        elif msg_type == "button":
            user_input = message["button"]["payload"].strip().lower()
        elif msg_type == "interactive":
            interactive = message.get("interactive", {})
            if interactive.get("type") == "button_reply":
                user_input = interactive["button_reply"]["id"].strip().lower()
        handled = await handle_parent_selection(phone, user_input)
        if handled:
            return {"status": "ok"}
        if user_input in ["start", "hi", "hello"]:
            await send_welcome_template(phone)
        elif user_input == "new_here" or user_input == "New here" or  user_input == "New Here" or user_input == "new here":
            await handle_new_here(phone)
        elif user_input == "parent":
            await handle_parent(phone)
        elif user_input == "present_status":
            await handle_present_status(phone)
        elif user_input == "notices":
            await handle_notices(phone)
        elif user_input == "more_parent":
            await show_parent_other_menu(phone)
        elif user_input == "warnings":
            await handle_warnings(phone)
        elif user_input == "meetings":
            await handle_meetings(phone)            
        elif user_input == "fees_parent":
            await handle_parent_fees(phone)
        elif user_input == "principal":
            await handle_principal(phone)
        elif user_input == "other":
            await handle_other_menu(phone)
        elif user_input == "attendance":
            await handle_attendance(phone)
        elif user_input == "fees":
            await handle_finance(phone)
        elif user_input == "idcard":
            await handle_idcard_status(phone)
        elif user_input == "admin":
            await handle_admin(phone)
        elif user_input == "superadmin":
            await handle_superadmin(phone)
        elif user_input == "all_schools":
            await handle_all_schools(phone)
        elif user_input == "all_schools":
            await handle_all_schools(phone)
        elif user_input == "all_orders":
            await handle_all_orders(phone)
        elif user_input == "oversee_total":
            await handle_admin_warnings(phone)
    except Exception as e:
        print("Parsing error:", e)
    return {"status": "ok"}


async def handle_new_here(phone):

    try:
        message = """
🌟 *Welcome to Student Next Light*

Student Next Light is a complete *School Management System* designed to make education smarter, faster, and more connected.

━━━━━━━━━━━━━━━━━━

📚 *What we offer:*

✅ Smart Attendance (Real-time Check IN/OUT)  
✅ Parent Notifications & Alerts  
✅ Fees Management & Reports  
✅ Notices & Announcements  
✅ ID Card & Gate Automation  
✅ Full School ERP System  

━━━━━━━━━━━━━━━━━━

📲 *Download Our Apps:*

👨‍🎓 *Student App*  
https://play.google.com/store/apps/details?id=com.starwish.student_managment_app&hl=en_IN  

👨‍👩‍👧 *Parents App*  
https://play.google.com/store/apps/details?id=com.starwish.parents_next_lights&hl=en_IN  

━━━━━━━━━━━━━━━━━━

📞 *For Demo / Pricing / Login Details:*  
Call or WhatsApp: +91 7000994158  

━━━━━━━━━━━━━━━━━━

We’re here to help your school go *digital & smart* 🚀
"""

        await send_text(phone, message)

    except Exception as e:
        print("New Here Error:", e)
        await send_text(phone, "⚠️ Unable to load information right now.")