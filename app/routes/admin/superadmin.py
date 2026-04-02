


from firebase_admin import firestore
import httpx


from app.services.whatsapp_service import BASE_URL, TOKEN, send_text

def clean_phone(phone: str):
    phone = phone.replace("+", "")
    if phone.startswith("91"):
        phone = phone[2:]
    return phone

def get_user_role(phone):
    db = firestore.client()
    doc = db.collection("railwayusers").document(phone).get()
    if doc.exists:
        return doc.to_dict().get("role")
    return None

async def handle_all_schools(phone):
    db = firestore.client()
    try:
        role = get_user_role(phone)

        if role != "superadmin":
            await send_text(phone, "❌ Access denied.")
            return
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

        if clean != "7000994158":
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
                {"id": "all_schools", "title": "All_Schools"},
                {"id": "all_orders", "title": "All_Orders"},
                {"id": "oversee_total", "title": "Oversee_Total"},
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

async def handle_all_orders(phone):
    db = firestore.client()
    try:
        role = get_user_role(phone)

        if role != "superadmin":
            await send_text(phone, "❌ Access denied.")
            return

        base_ref = db.collection("Admin").document("Order")

        completed = len(list(base_ref.collection("Completed").stream()))
        orders = len(list(base_ref.collection("Orders").stream()))
        progress = len(list(base_ref.collection("Progress").stream()))

        message = f"""
📦 *All Orders Summary*

━━━━━━━━━━━━━━━━━━

✅ Completed : {completed}
📥 Orders : {orders}
🔄 In Progress : {progress}
"""

        await send_text(phone, message)

    except Exception as e:
        print("Orders Error:", e)
        await send_text(phone, "⚠️ Unable to fetch orders.")

async def handle_admin_warnings(phone):
    db = firestore.client()
    try:
        role = get_user_role(phone)

        if role != "superadmin":
            await send_text(phone, "❌ Access denied.")
            return

        doc = db.collection("Admin").document("Order").get()

        if not doc.exists:
            await send_text(phone, "⚠️ No Overview data found.")
            return

        data = doc.to_dict()

        message = "⚠️ *Overview for Schools*\n\n"
        priority_keys = ["School", "College", "University"]
        
        for key in priority_keys:
            if key in data and isinstance(data[key], list):
                message += f"🏫 {key} : {len(data[key])}\n"
        message += "\n━━━━━━━━━━━━━━━━━━\n\n"

        for key, value in data.items():
            if key in priority_keys:
                continue
            if not isinstance(value, list):
                continue
            message += f"📍 {key} : {len(value)}\n"
        await send_text(phone, message)

    except Exception as e:
        print("Warnings Error:", e)
        await send_text(phone, "⚠️ Unable to fetch Overview")