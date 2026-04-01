from app.firebase_client import db
from app.services.whatsapp_service import send_text
import httpx
import os

TOKEN = os.getenv("WHATSAPP_API_KEY")
BASE_URL = "https://live.theautomate.ai"


def clean_phone(phone: str):
    phone = phone.replace("+", "")
    if phone.startswith("91"):
        phone = phone[2:]
    return phone


async def handle_parent(phone):

    try:
        clean = clean_phone(phone)

        found_student = None
        school_name = ""

    
        schools = db.collection("School").stream()

        for school in schools:
            school_data = school.to_dict()
            students = db.collection("School") \
                .document(school.id) \
                .collection("Students") \
                .stream()

            for s in students:
                data = s.to_dict()

                if data.get("Mobile") == clean:
                    found_student = data
                    school_name = school_data.get("Name", "School")
                    break

            if found_student:
                break

        if not found_student:
            await send_text(phone, "⚠️ No student found linked to this number.")
            return

        
        name = found_student.get("Name", "Student")
        father = found_student.get("Father_Name", "")
        student_class = found_student.get("Class", "")
        section = found_student.get("Section", "")
        roll = found_student.get("Roll_number", "")
        status = found_student.get("State", "Unknown")
        address = found_student.get("Datima", "")

      
        message = f"""
👋 Hello, Parent of *{name}*

🏫 {school_name}

━━━━━━━━━━━━━━━━━━

🎓 Class : {student_class} - {section}
🪪 Roll No : {roll}

👨 Father : {father}

📍 Address : {address}

━━━━━━━━━━━━━━━━━━

📊 Current Status : {status}
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
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient() as client:
            await client.post(
                f"{BASE_URL}/api/send",
                json=payload,
                headers=headers
            )

    except Exception as e:
        print("Parent Error:", e)
        await send_text(phone, "⚠️ Unable to fetch student details right now.")