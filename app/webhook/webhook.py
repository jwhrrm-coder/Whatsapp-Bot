

from fastapi import FastAPI, Request
import json




app = FastAPI()
@app.post("/webhook")
async def webhook(request: Request):

    payload = await request.json()
    print(json.dumps(payload, indent=2))

    # ignore events that are not user messages
    if payload.get("event") != "message.received":
        return {"status": "ignored"}

    try:
        message = payload["data"]["data"]["value"]["messages"][0]

        phone = message["from"]
        if not phone.startswith("+"):
            phone = "+" + phone

        msg_type = message["type"]

        # TEXT
        if msg_type == "text":
            text = message["text"]["body"].lower()

            if text == "start" or text == "Hi" or text == "Hello" or text == "hello" or text == "hi":
                await send_welcome_template(phone)

        # BUTTON CLICK

        elif msg_type == "button":

            button = message["button"]["payload"]
            if button.lower() == "principal":
                clean = clean_phone(phone)
                school = get_school_by_phone(clean)
                if school:
                    await send_principal_menu(phone, school)
        else:
            await send_text(phone, "School not registered.")
            if button == "New Here":
                await send_text(phone, "👋 Welcome new user!")

            elif button == "Parent":
                await send_text(phone, "👨‍👩‍👧 Parent services info.")

            elif button == "Principal":
                await send_text(phone, "🏫 Principal dashboard info.")

    except Exception as e:
        print("Parsing error:", e)

    return {"status": "ok"}

def clean_phone(phone):
    phone = phone.replace("+", "")

    if phone.startswith("91"):
        phone = phone[2:]

    return phone