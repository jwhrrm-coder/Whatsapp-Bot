import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

# load service account from env variable
cred_dict = json.loads(os.getenv("FIREBASE_SERVICE_ACCOUNT"))

cred = credentials.Certificate(cred_dict)
firebase_admin.initialize_app(cred)

db = firestore.client()