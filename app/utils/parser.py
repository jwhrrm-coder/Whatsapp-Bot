def parse_message(data):

    try:
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]

        message = value["messages"][0]["text"]["body"]
        phone = value["messages"][0]["from"]

        return phone, message

    except:
        return None, None