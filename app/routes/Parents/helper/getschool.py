from firebase_client import db

def get_school_by_phone(phone):

    school_ref = db.collection("School").where("Phone", "==", phone).limit(1)
    docs = school_ref.stream()

    for doc in docs:
        return doc.to_dict()

    return None