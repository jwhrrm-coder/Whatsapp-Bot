


import httpx
import os
from app.firebase_client import db
from app.routes.Parents.parent_handler import clean_phone
from app.services.whatsapp_service import send_text





async def handle_admin(phone):

    try:
        clean = clean_phone(phone)

        schools_ref = db.collection("School").stream()

        found_schools = []

        for s in schools_ref:
            data = s.to_dict()

            if data.get("Phone") == clean:
                found_schools.append(data)

        if not found_schools:
            await send_text(phone, "⚠️ No schools linked to this Admin.")
            return

        # 💾 SAVE SESSION
        db.collection("railwayusers").document(phone).set({
            "role": "admin"
        }, merge=True)

        # 📩 MESSAGE
        message = "Welcome Admin to our Smart School Managment System. We Weclome you to the admin panel of your school. Here you can view all the details of your school and manage it effectively. \n\n🏫 *Your Schools are : *\n\n"

        for i, s in enumerate(found_schools, start=1):
            message += f"""
{i}️⃣ *{s.get("Name","")}*

📞 Phone: {s.get("Phone","")}
👨‍🎓 Students: {s.get("totse",0)}
📩 SMS Enabled: {s.get("smsend", False)}
💎 Premium: {s.get("premium", False)}

━━━━━━━━━━━━━━━━━━
"""

        await send_text(phone, message)

    except Exception as e:
        print("Admin Error:", e)
        await send_text(phone, "⚠️ Unable to fetch admin data.")

