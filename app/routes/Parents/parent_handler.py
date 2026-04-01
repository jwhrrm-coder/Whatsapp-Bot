


import httpx

from app.firebase_client import db
from app.routes.School.helper import get_school_by_phone
from app.services.whatsapp_service import send_text

def clean_phone(phone: str):
    phone = phone.replace("+", "")
    if phone.startswith("91"):
        phone = phone[2:]
    return phone

async def handle_parent(phone):
    await send_text(phone, "Please wait while we fetch your linked students...")
    try:
        clean = clean_phone(phone)

        students_found = []

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
                    students_found.append({
                        "student_id": s.id,
                        "school_id": school.id,
                        "school_name": school_data.get("Name", "School"),
                        "name": data.get("Name", ""),
                        "class": data.get("Class", ""),
                        "section": data.get("Section", ""),
                    })

        if not students_found:
            await send_text(phone, "⚠️ No students found linked to this number.")
            return

        db.collection("railwayusers").document(phone).set({
            "role": "parent_select",
            "students_list": students_found
        }, merge=True)
        message = "👨‍👩‍👧 *Your Children:*\n\n"

        for i, s in enumerate(students_found, start=1):
            message += f"{i}️⃣ {s['name']} ({s['class']} - {s['section']})\n"

        message += "\nReply with number (1/2/3...) to select student"

        await send_text(phone, message)

    except Exception as e:
        print("Parent List Error:", e)
        await send_text(phone, "⚠️ Error fetching student list.")