import os
import json
import random
import string

def get_watermark():
    if os.path.exists("wm.json"):
        with open("wm.json") as f:
            data = json.load(f)
        return data.get("path")

def save_watermark(path):
    with open("wm.json", "w") as f:
        json.dump({"path": path}, f)

def caption_enabled():
    if os.path.exists("caption.json"):
        with open("caption.json") as f:
            return json.load(f).get("enabled", True)
    return True

def toggle_caption():
    current = caption_enabled()
    with open("caption.json", "w") as f:
        json.dump({"enabled": not current}, f)
    return not current

def is_owner(user_id):
    return user_id == 7537050026

def generate_code():
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    data = {}
    if os.path.exists("codes.json"):
        with open("codes.json") as f:
            data = json.load(f)
    data[code] = {"used": False}
    with open("codes.json", "w") as f:
        json.dump(data, f)
    return code

def validate_code(code, user_id):
    if not os.path.exists("codes.json"):
        return "❌ No codes found."
    with open("codes.json") as f:
        codes = json.load(f)

    if code not in codes:
        return "❌ Invalid code."

    if codes[code]["used"]:
        return "⚠️ Code already used."

    if not os.path.exists("claimed.json"):
        claimed = []
    else:
        with open("claimed.json") as f:
            claimed = json.load(f)

    claimed.append(str(user_id))

    with open("claimed.json", "w") as f:
        json.dump(claimed, f)

    codes[code]["used"] = True
    with open("codes.json", "w") as f:
        json.dump(codes, f)

    return "✅ Code claimed! Watermarking is now active in your channel."
