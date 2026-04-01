# ==================================
# 🔹 SUPER ADMIN HANDLER
# ==================================
from firebase_admin import db
import httpx


from app.services.whatsapp_service import BASE_URL, TOKEN, send_text

def clean_phone(phone: str):
    phone = phone.replace("+", "")
    if phone.startswith("91"):
        phone = phone[2:]
    return phone
async def handle_superadmin(phone):

    try:
        clean = clean_phone(phone)

        if clean != "8093426959":
            await   send_text(
                phone,
                "❌ You are not Jawahar Ram or any Manager under Next Light.\nAccess Denied."
            )
            return

        # 💾 SAVE SESSION
        db.collection("railwayusers").document(phone).set({
            "role": "superadmin"
        }, merge=True)

        # 📲 BUTTON MENU
        payload = {
            "phone": phone,
            "message": "👑 Welcome Super Admin Panel",
            "buttons": [
                {"id": "all_schools", "title": "All Schools"},
                {"id": "all_orders", "title": "All Orders"},
                {"id": "warnings_admin", "title": "Warnings"},
            ]
        }

        headers = {
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient() as client:
            await client.post(f"{BASE_URL}/api/send", json=payload, headers=headers)

    except Exception as e:
        print("SuperAdmin Error:", e)
        await send_text(phone, "⚠️ Error loading Super Admin panel.")

async def handle_all_schools(phone):

    try:
        schools_ref = db.collection("School").stream()

        message = "🌍 *All Schools Overview*\n\n"

        for i, s in enumerate(schools_ref, start=1):
            data = s.to_dict()

            message += f"""
{i}️⃣ *{data.get("Name","")}*

📞 Phone: {data.get("Phone","")}
👨‍🎓 Students: {data.get("totse",0)}
📩 SMS Enabled: {data.get("smsend", False)}
💎 Premium: {data.get("premium", False)}

━━━━━━━━━━━━━━━━━━
"""

        await send_text(phone, message)

    except Exception as e:
        print("All Schools Error:", e)
        await send_text(phone, "⚠️ Unable to fetch schools.")