import os
import httpx

TOKEN = os.getenv("WHATSAPP_API_KEY")
BASE_URL = "https://live.theautomate.ai"


async def send_welcome_template(phone):

    message = """🌟 STUDIO NEXT LIGHT में आपका स्वागत है!

हमें खुशी है कि आप हमारे साथ
📚 Smart Education & Smart Security
🎥 Photo & Video Service
की नई शुरुआत कर रहे हैं।

━━━━━━━━━━━━━━━━━━
🏫 Schools/Colleges के लिए हमारी विशेष सेवाएँ:

✅ Smart ID Card (QR Based)
• Gate पर Scan
• Entry/Exit Auto Record
• Parents को SMS Alert

✅ Complete School ERP System
Attendance | Fees | Timetable | Exam | Result | Bus | Hostel – सब एक ही जगह।

✅ Real-Time Alerts
Student स्कूल आए या जाए – Parents को तुरंत अपडेट।

✅ Transparent & Affordable
Per Student Clear Pricing – कोई Hidden Charge नहीं।

✅ Proven Experience
800+ Students के लिए Government School में सफल Implementation।

━━━━━━━━━━━━━━━━━━
🤝 हमारे साथ आप क्या देख रहे हैं?
1️⃣ School/College Smart Services
2️⃣ Professional Photo & Video Services

अधिक जानकारी के लिए Reply करें या Call करें।
धन्यवाद 🙏
"""

    payload = {
        "phone": phone,
        "message": message,
        "buttons": [
            {"id": "new here", "title": "New here"},
            {"id": "parent", "title": "Parent"},
            {"id": "principal", "title": "Principal"}
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

async def send_text(phone, text):

    payload = {
        "phone": phone,
        "message": text
    }

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/send",
            json=payload,
            headers=headers
        )

    print("Text response:", response.text)