from app.firebase_client import db


def get_school_by_phone(phone):

    docs = db.collection("School").where("Phone", "==", phone).limit(1).stream()

    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id   # add document id
        return data

    return None

def get_user_school(phone):

    doc = db.collection("railwayusers").document(phone).get()

    if doc.exists:
        return doc.to_dict().get("school_id")

    return None