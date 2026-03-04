from app.services.whatsapp_service import send_message


async def handle_message(phone, message):

    msg = message.lower()

    if msg == "hi" or msg == "hello":

        text = """
Welcome 👋

Choose an option:

1️⃣ Products
2️⃣ Support
"""

        send_message(phone, text)

    elif msg == "1":

        send_message(phone, "You selected Products")

    elif msg == "2":

        send_message(phone, "You selected Support")

    else:

        send_message(phone, "Please select 1 or 2")