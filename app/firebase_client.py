import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

cred_dict = json.loads(os.getenv("FIREBASE_SERVICE_ACCOUNT"))

cred_dict["private_key"] = cred_dict["private_key"].replace("\\n", "\n")

cred = credentials.Certificate(cred_dict)

firebase_admin.initialize_app(cred)

db = firestore.client()