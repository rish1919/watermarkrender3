import json, os

CODES_FILE = "codes.json"
WATERMARK_PATH = "watermarks/watermark.png"
OWNER_ID = 7537050026

def is_owner(user_id):
    return user_id == OWNER_ID

def set_watermark(path):
    os.makedirs("watermarks", exist_ok=True)
    with open("wm.json", "w") as f:
        json.dump({"path": path}, f)

def get_watermark():
    if os.path.exists("wm.json"):
        with open("wm.json") as f:
            data = json.load(f)
        return data.get("path")

def delete_watermark():
    if os.path.exists("wm.json"):
        os.remove("wm.json")

def load_code_data():
    if os.path.exists(CODES_FILE):
        with open(CODES_FILE) as f:
            return json.load(f)
    return {}

def save_code_data(data):
    with open(CODES_FILE, "w") as f:
        json.dump(data, f)

def is_authorized_channel(chat_id):
    data = load_code_data()
    for _, entry in data.items():
        if entry.get("channel_id") == chat_id:
            return True
    return False

def verify_code(code, user_id):
    data = load_code_data()
    if code not in data:
        return False, "❌ Invalid or expired code."
    if data[code].get("used"):
        return False, "❌ Code already used."
    data[code]["used"] = True
    data[code]["channel_id"] = user_id
    save_code_data(data)
    return True, "✅ Code claimed. You can now use watermark features in your channel."
