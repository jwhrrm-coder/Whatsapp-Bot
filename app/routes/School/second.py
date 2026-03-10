import datetime
from zoneinfo import ZoneInfo

from app.firebase_client import db
from app.routes.School.helper import get_user_school
from app.services.whatsapp_service import send_text


async def handle_attendance(phone):

    try:
        school_id = get_user_school(phone)

        if not school_id:
            await send_text(phone, "⚠️ Session expired. Please type *Principal* again.")
            return

        school_doc = db.collection("School").document(school_id).get().to_dict()

        if not school_doc:
            await send_text(phone, "⚠️ School data not found.")
            return

        session_id = school_doc.get("cse")

        if not session_id:
            await send_text(phone, "⚠️ Current session not configured.")
            return

        # TOTAL STUDENTS
        sessions = db.collection("School").document(school_id).collection("Session").stream()

        total_students = 0
        for s in sessions:
            data = s.to_dict()
            total_students += int(data.get("feet", 0))

        # CHECK IN & CHECK OUT
        classes = db.collection("School").document(school_id) \
            .collection("Session").document(session_id) \
            .collection("Class").stream()

        checkin = 0
        checkout = 0

        for c in classes:
            data = c.to_dict()
            checkin += int(data.get("pcount", 0))
            checkout += int(data.get("pcount1", 0))

        # LEAVE
        leave_docs = db.collection("School").document(school_id) \
            .collection("Session").document(session_id) \
            .collection("Leave").stream()

        leave = len(list(leave_docs))

        pending_out = checkin - checkout
        absent = total_students - checkin - leave

        now = datetime.datetime.now(ZoneInfo("Asia/Kolkata"))
        formatted_time = now.strftime("%d %b %I:%M %p")

        message = f"""
📊 *Attendance Summary*
as of {formatted_time}

👨‍🎓 Total Students: {total_students}

✅ Check IN : {checkin}
🚪 Check OUT : {checkout}

⏳ Pending OUT : {pending_out}

🏖 Leave : {leave}
❌ Absent : {absent}
"""

        await send_text(phone, message)

    except Exception as e:
        print("Attendance Error:", e)
        await send_text(phone, "⚠️ Unable to fetch attendance data right now. Please try again later.")

async def handle_finance(phone):

    try:
        school_id = get_user_school(phone)

        if not school_id:
            await send_text(phone, "⚠️ Session expired. Please type *Principal* again.")
            return

        school_doc = db.collection("School").document(school_id).get().to_dict()

        if not school_doc:
            await send_text(phone, "⚠️ School information not found.")
            return

        school_name = school_doc.get("Name", "School")
        session_id = school_doc.get("cse")

        now = datetime.datetime.now()
        year = str(now.year)
        month = str(now.month)

        # TOTAL STUDENTS
        classes = db.collection("School") \
            .document(school_id) \
            .collection("Session") \
            .document(session_id) \
            .collection("Class") \
            .stream()

        students = 0
        for c in classes:
            data = c.to_dict()
            students += int(data.get("feet", 0))

        # MONTHLY COLLECTION
        days = db.collection("School") \
            .document(school_id) \
            .collection("Fee") \
            .document(year) \
            .collection("Month") \
            .document(month) \
            .collection("Day") \
            .stream()

        monthly = 0
        for d in days:
            data = d.to_dict()
            monthly += int(data.get("Total_Fee", 0))

        # YEARLY COLLECTION
        months = db.collection("School") \
            .document(school_id) \
            .collection("Fee") \
            .document(year) \
            .collection("Month") \
            .stream()

        yearly = 0
        for m in months:
            data = m.to_dict()
            yearly += int(data.get("Fee", 0))

        expected = students * 500
        due = expected - yearly

        message = f"""
💰 *School Finance Report*
🏫 {school_name}

👨‍🎓 Students : {students}

💳 Expected Fee : ₹{expected}

⚠️ Pending Fee : ₹{due}

📅 This Month : ₹{monthly}

📆 This Year : ₹{yearly}
"""

        await send_text(phone, message)

    except Exception as e:
        print("Finance Error:", e)
        await send_text(phone, "⚠️ Unable to fetch finance data right now.")


async def handle_idcard_status(phone):

    try:
        school_id = get_user_school(phone)

        if not school_id:
            await send_text(phone, "⚠️ Session expired. Please type *Principal* again.")
            return

        school_doc = db.collection("School").document(school_id).get().to_dict()

        if not school_doc:
            await send_text(phone, "⚠️ School record not found.")
            return

        session_id = school_doc.get("cse")
        school_name = school_doc.get("Name", "School")

        classes_ref = db.collection("School") \
            .document(school_id) \
            .collection("Session") \
            .document(session_id) \
            .collection("Class") \
            .stream()

        classes = list(classes_ref)

        if not classes:
            await send_text(phone, "⚠️ No classes found for current session.")
            return

        message = f"🎓 *ID Card Status*\n🏫 {school_name}\n\n"

        for c in classes:
            data = c.to_dict()

            class_name = data.get("Name", c.id)
            status = data.get("status", "❌ Not Generated")

            message += f"{class_name} : {status}\n"

        await send_text(phone, message)

    except Exception as e:
        print("ID Card Status Error:", e)
        await send_text(phone, "⚠️ Unable to fetch ID card status right now.")