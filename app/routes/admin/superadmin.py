


from firebase_admin import firestore
import httpx


from app.services.whatsapp_service import BASE_URL, TOKEN, send_text

def clean_phone(phone: str):
    phone = phone.replace("+", "")
    if phone.startswith("91"):
        phone = phone[2:]
    return phone

async def handle_all_schools(phone):
    db = firestore.client()
    try:
        schools_ref = db.collection("School").stream()

        messages = []
        current_chunk = "🌍 *All Schools Overview*\n\n"

        for i, s in enumerate(schools_ref, start=1):
            data = s.to_dict()

            entry = f"""
{i}️⃣ *{data.get("Name","")}*

📞 Phone: {data.get("Phone","")}
👨‍🎓 Students: {data.get("totse",0)}
📩 SMS Enabled: {data.get("smsend", False)}
💎 Premium: {data.get("premium", False)}

━━━━━━━━━━━━━━━━━━
"""

            # 🔥 If adding this exceeds limit → push chunk
            if len(current_chunk) + len(entry) > 3500:
                messages.append(current_chunk)
                current_chunk = ""

            current_chunk += entry

        # add last chunk
        if current_chunk:
            messages.append(current_chunk)

        # 📤 SEND ALL PARTS
        for msg in messages:
            await send_text(phone, msg)

    except Exception as e:
        print("All Schools Error:", e)
        await send_text(phone, "⚠️ Unable to fetch schools.")
async def handle_superadmin(phone):
    db = firestore.client()
    try:
        clean = clean_phone(phone)

        if clean != "8093426959":
            await   send_text(
                phone,
                "❌ You are not Jawahar Ram or any Manager under Next Light.\nAccess Denied."
            )
            return

        db.collection("railwayusers").document(phone).set({
            "role": "superadmin"
        }, merge=True)

        payload = {
            "phone": phone,
            "message": "👑 Welcome Super Admin Panel as Jawahar Ram ! Please pic a Function to apply for Super Admin Function",
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

    db = firestore.client()
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