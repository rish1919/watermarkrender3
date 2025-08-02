import os
import json
import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from watermark_utils import apply_watermark_to_image, apply_watermark_to_video
from utils import load_config, save_config, is_owner, generate_code

logging.basicConfig(level=logging.INFO)

# ====== CONFIG ======
BOT_TOKEN = "8413346186:AAFnzBn8rnj32W6XGpA5uXJI3EBhKCvwpg0"
OWNER_ID = 7537050026
APP_ID = 20712463
APP_HASH = "bee29238bf0db4a82548c2ffe29d43c1"
CONFIG_FILE = "config.json"
CODES_FILE = "codes.json"

if not os.path.exists(CONFIG_FILE):
    save_config({})

if not os.path.exists(CODES_FILE):
    with open(CODES_FILE, "w") as f:
        json.dump({}, f)

config = load_config()
bot = Client("watermark_bot", api_id=APP_ID, api_hash=APP_HASH, bot_token=BOT_TOKEN)


# ====== UTILITY FUNCTIONS ======
def load_codes():
    with open(CODES_FILE, "r") as f:
        return json.load(f)


def save_codes(codes):
    with open(CODES_FILE, "w") as f:
        json.dump(codes, f, indent=4)


# ====== COMMANDS ======

@bot.on_message(filters.command("start"))
async def start(client, message: Message):
    await message.reply("👋 Welcome to the Watermark Bot.\n\nUse /claimcode <code> to activate watermarking in your channel.")


@bot.on_message(filters.command("setwm") & filters.user(OWNER_ID))
async def set_watermark(client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.document:
        return await message.reply("Please reply to a PNG file to set as watermark.")
    
    file = await message.reply_to_message.download(file_name="watermark.png")
    config["watermark_path"] = file
    save_config(config)
    await message.reply("✅ Watermark set successfully.")


@bot.on_message(filters.command("showwm"))
async def show_watermark(client, message: Message):
    wm = config.get("watermark_path")
    if wm and os.path.exists(wm):
        await message.reply_photo(photo=wm, caption="🖼 Current Watermark")
    else:
        await message.reply("❌ No watermark set.")


@bot.on_message(filters.command("dltwm") & filters.user(OWNER_ID))
async def delete_watermark(client, message: Message):
    wm = config.get("watermark_path")
    if wm and os.path.exists(wm):
        os.remove(wm)
    config["watermark_path"] = None
    save_config(config)
    await message.reply("🗑 Watermark deleted.")


@bot.on_message(filters.command("caption"))
async def toggle_caption(client, message: Message):
    status = message.text.split(" ")[-1].lower()
    if status == "on":
        config["caption"] = True
        await message.reply("✅ Captions will be included.")
    elif status == "off":
        config["caption"] = False
        await message.reply("🚫 Captions will be excluded.")
    else:
        await message.reply("Usage: `/caption on` or `/caption off`")
    save_config(config)


@bot.on_message(filters.command("claimcode"))
async def claim_code(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("Usage: `/claimcode CODE`")
    code = message.command[1].strip().upper()

    codes = load_codes()
    if code in codes and not codes[code]["used"]:
        chat_id = message.chat.id
        config["authorized_channel"] = chat_id
        codes[code]["used"] = True
        save_codes(codes)
        save_config(config)
        await message.reply("✅ Code claimed successfully. Watermarking is now active in this channel.")
    else:
        await message.reply("❌ Invalid or already used code.")


# ====== MEDIA HANDLING ======

@bot.on_message(filters.channel & filters.media)
async def watermark_handler(client, message: Message):
    if str(message.chat.id) != str(config.get("authorized_channel")):
        return  # Not authorized

    wm_path = config.get("watermark_path")
    if not wm_path or not os.path.exists(wm_path):
        return

    try:
        if message.photo:
            output = await apply_watermark_to_image(message, wm_path)
            await message.reply_photo(output, caption=message.caption if config.get("caption", True) else None)
        elif message.video:
            output = await apply_watermark_to_video(message, wm_path)
            await message.reply_video(output, caption=message.caption if config.get("caption", True) else None)
    except Exception as e:
        logging.exception("Watermarking failed")
        await message.reply("❌ Failed to apply watermark.")


# ====== START ======
bot.run()
