


import httpx
import os
from app.firebase_client import db
from app.services.whatsapp_service import send_text
TOKEN = os.getenv("WHATSAPP_API_KEY")
BASE_URL = "https://live.theautomate.ai"
async def handle_parent_selection(phone, user_input):

    try:
        user_doc = db.collection("railwayusers").document(phone).get().to_dict()

        if not user_doc or user_doc.get("role") != "parent_select":
            return False  # not handled here

        students = user_doc.get("students_list", [])

        index = int(user_input) - 1

        if index < 0 or index >= len(students):
            await send_text(phone, "⚠️ Invalid selection. Please try again.")
            return True

        selected = students[index]

        # 💾 SAVE FINAL SESSION
        db.collection("railwayusers").document(phone).set({
            "role": "parent",
            "school_id": selected["school_id"],
            "student_id": selected["student_id"],
            "student_name": selected["name"],
            "class": selected["class"],
        }, merge=True)

        # 🎯 CALL DETAILS VIEW
        await show_selected_student(phone, selected)

        return True

    except Exception as e:
        print("Selection Error:", e)
        await send_text(phone, "⚠️ Error selecting student.")
        return True
    
async def show_selected_student(phone, student):

    message = f"""
👋 Hello, Parent of *{student['name']}*

🏫 {student['school_name']}

━━━━━━━━━━━━━━━━━━

🎓 Class : {student['class']} - {student['section']}

📊 Status : ACTIVE

━━━━━━━━━━━━━━━━━━

Choose option:
"""

    payload = {
        "phone": phone,
        "message": message,
        "buttons": [
            {"id": "present_status", "title": "Present Status"},
            {"id": "notices", "title": "Notices"},
            {"id": "fees_parent", "title": "Fees"},
        ]
    }

    headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    }

    async with httpx.AsyncClient() as client:
        await client.post(f"{BASE_URL}/api/send", json=payload, headers=headers)