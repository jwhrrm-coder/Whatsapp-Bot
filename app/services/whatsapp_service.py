import requests
from app.config import ACCESS_TOKEN, PHONE_NUMBER_ID

URL = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"

def send_message(phone, text):

    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "text",
        "text": {"body": text}
    }

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    requests.post(URL, json=payload, headers=headers)