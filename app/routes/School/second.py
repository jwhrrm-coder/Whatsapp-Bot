import datetime
from zoneinfo import ZoneInfo

from app.firebase_client import db
from app.routes.School.helper import get_user_school
from app.services.whatsapp_service import send_text


async def handle_attendance(phone):

    school_id = get_user_school(phone)

    if not school_id:
        await send_text(phone, "Session expired. Please type *Principal* again.")
        return

    school_doc = db.collection("School").document(school_id).get().to_dict()
    session_id = school_doc.get("csession")

    # TOTAL STUDENTS
    sessions = db.collection("School").document(school_id).collection("Session").stream()

    total_students = 0
    for s in sessions:
        data = s.to_dict()
        total_students += data.get("feet", 0)

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

    # CALCULATIONS
    pending_out = checkin - checkout
    absent = total_students - checkin - leave
    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    formatted_time = now.strftime("%d %b %I:%M %p")
    message = f"""
📊 *Attendance Summary* for your School as of {formatted_time} :

👨‍🎓 Total Students: {total_students}

✅ Check IN (Present): {checkin}
🚪 Check OUT: {checkout}

⏳ Pending OUT: {pending_out}

🏖 Leave: {leave}
❌ Absent: {absent}
"""

    await send_text(phone, message)


async def handle_finance(phone):

    school_id = get_user_school(phone)

    if not school_id:
        await send_text(phone, "Session expired. Please type *Principal* again.")
        return

    school_doc = db.collection("School").document(school_id).get().to_dict()
    school_name = school_doc.get("Name", "School")
    session_id = school_doc.get("csession")

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

    # Example expected fee calculation
    expected = students * 500   # adjust if needed

    due = expected - yearly

    message = f"""
💰 *School Finance Report* for 🏫 {school_name}

━━━━━━━━━━━━━━━━━━

👨‍🎓 Students in Session: {students}

📊 *Fee Overview*

💳 Expected Fee (Session) : ₹{expected}

⚠️ Pending / Due Fee : ₹{due}

📅 This Month Paid : ₹{monthly}

📆 This Year Paid : ₹{yearly}
"""

    await send_text(phone, message)

async def handle_idcard_status(phone):

    school_id = get_user_school(phone)

    if not school_id:
        await send_text(phone, "Session expired. Please type *Principal* again.")
        return

    # Get school document
    school_doc = db.collection("School").document(school_id).get().to_dict()

    session_id = school_doc.get("csession")
    school_name = school_doc.get("Name", "School")

    # Get all classes
    classes_ref = db.collection("School") \
        .document(school_id) \
        .collection("Session") \
        .document(session_id) \
        .collection("Class") \
        .stream()

    message = f"🎓 *ID Card Status*\n for 🏫 {school_name}\n\n"

    for c in classes_ref:
        data = c.to_dict()

        class_name = data.get("Name", c.id)
        status = data.get("ou", "Unknown")

        message += f"{class_name} : {status}\n"

    await send_text(phone, message)