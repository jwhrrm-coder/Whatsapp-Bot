


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
            await send_text(phone, "⚠️ Please select the Correct Student Name")
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
👋 Hello, Parent of *{student['name']}*. Welcome to Smart School Managment System of🏫 {student['school_name']}

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
            {"id": "present_status", "title": "Check In Details"},
            {"id": "notices", "title": "Notices"},
            {"id": "more_parent", "title": "Other"},
        ]
    }

    headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    }

    async with httpx.AsyncClient() as client:
        await client.post(f"{BASE_URL}/api/send", json=payload, headers=headers)



# ===============================
# 🔹 GET USER SESSION
# ===============================
def get_parent_session(phone):
    doc = db.collection("railwayusers").document(phone).get()
    return doc.to_dict() if doc.exists else None



# ===============================
# 🔹 SUB MENU (OTHER)
# ===============================
async def show_parent_other_menu(phone):

    payload = {
        "phone": phone,
        "message": "Choose additional options:",
        "buttons": [
            {"id": "warnings", "title": "Warnings"},
            {"id": "meetings", "title": "Parents Meeting"},
            {"id": "fees_parent", "title": "Fees"},
        ]
    }

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        await client.post(f"{BASE_URL}/api/send", json=payload, headers=headers)


# ===============================
# 🔹 FEES (FOR NOW STATIC)
# ===============================
async def handle_parent_fees(phone):

    await send_text(phone, "💰 Fees Due: ₹0\n\n(No pending fees 🎉)")


# ===============================
# 🔹 COMMON NOTICE FETCHER
# ===============================
async def fetch_notices(phone, collection_name, title):

    try:
        user = get_parent_session(phone)

        if not user:
            await send_text(phone, "⚠️ Session expired.")
            return

        school_id = user.get("school_id")
        student_id = user.get("student_id")

        # 🔥 GET STUDENT DATA
        student_doc = db.collection("School") \
            .document(school_id) \
            .collection("Students") \
            .document(student_id) \
            .get()

        student = student_doc.to_dict()

        class_id = student.get("Classn")

        # 🔥 GET SESSION
        school_doc = db.collection("School").document(school_id).get().to_dict()
        session_id = school_doc.get("cse")

        # 🔥 FETCH NOTICES
        notices_ref = db.collection("School") \
            .document(school_id) \
            .collection("Session") \
            .document(session_id) \
            .collection("Class") \
            .document(class_id) \
            .collection(collection_name) \
            .stream()

        notices = []

        for n in notices_ref:
            data = n.to_dict()
            notices.append(data)

        if not notices:
            await send_text(phone, f"📭 No {title} available.")
            return

        # 🔥 SORT BY DATE (latest first)
        notices = sorted(notices, key=lambda x: x.get("date2", ""), reverse=True)

        message = f"📢 *Latest {title}*\n\n"

        for i, n in enumerate(notices[:5], start=1):
            message += f"""
{i}️⃣ *{n.get("name", "")}*
📝 {n.get("description", "")}
📅 {n.get("date", "")}

"""

        await send_text(phone, message)

    except Exception as e:
        print(f"{title} Error:", e)
        await send_text(phone, f"⚠️ Unable to fetch {title}.")


# ===============================
# 🔹 NOTICE TYPES
# ===============================
async def handle_notices(phone):
    await fetch_notices(phone, "Notice", "Notices")


async def handle_warnings(phone):
    await fetch_notices(phone, "Warnings", "Warnings")


async def handle_meetings(phone):
    await fetch_notices(phone, "Parents Meeting", "Meetings")


# ===============================
# 🔹 PRESENT STATUS (placeholder)
# ===============================
async def handle_present_status(phone):

    await send_text(phone, "📊 Fetching today's check-in details...\n(Will implement next 👀)")