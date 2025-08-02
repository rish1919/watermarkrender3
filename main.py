import os
import json
from pyrogram import Client, filters
from pyrogram.types import Message
from watermark_utils import add_watermark_to_image, add_watermark_to_video
from utils import (
    is_owner,
    get_watermark,
    caption_enabled,
    toggle_caption,
    save_watermark,
    generate_code,
    validate_code,
)
import logging

API_ID = 20712463
API_HASH = "bee29238bf0db4a82548c2ffe29d43c1"
BOT_TOKEN = "8413346186:AAFnzBn8rnj32W6XGpA5uXJI3EBhKCvwpg0"
OWNER_ID = 7537050026

bot = Client("watermarkbot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

logging.basicConfig(level=logging.INFO)

@bot.on_message(filters.command("start"))
async def start(_, msg: Message):
    await msg.reply("👋 Welcome to Watermark Bot!\n\nUse /claimcode <code> to activate it in your channel.")

@bot.on_message(filters.command("claimcode") & filters.private)
async def claim(_, msg: Message):
    if len(msg.command) < 2:
        return await msg.reply("❌ Please provide a claim code.")
    code = msg.command[1]
    user_id = msg.from_user.id
    result = validate_code(code, user_id)
    await msg.reply(result)

@bot.on_message(filters.command("generatecode") & filters.user(OWNER_ID))
async def generate(_, msg: Message):
    code = generate_code()
    await msg.reply(f"✅ Generated Code:\n`{code}`")

@bot.on_message(filters.command("setwm") & filters.user(OWNER_ID) & filters.reply)
async def set_wm(_, msg: Message):
    file = msg.reply_to_message
    if file.photo or file.document:
        path = await file.download()
        save_watermark(path)
        await msg.reply("✅ Watermark saved successfully.")
    else:
        await msg.reply("❌ Please reply to a PNG image.")

@bot.on_message(filters.command("showwm") & filters.user(OWNER_ID))
async def show_wm(_, msg: Message):
    path = get_watermark()
    if path and os.path.exists(path):
        await msg.reply_photo(path, caption="📌 Current Watermark:")
    else:
        await msg.reply("⚠️ No watermark found.")

@bot.on_message(filters.command("dltwm") & filters.user(OWNER_ID))
async def delete_wm(_, msg: Message):
    path = get_watermark()
    if path and os.path.exists(path):
        os.remove(path)
        await msg.reply("✅ Watermark deleted.")
    else:
        await msg.reply("⚠️ No watermark to delete.")

@bot.on_message(filters.command("caption") & filters.user(OWNER_ID))
async def toggle_caption_cmd(_, msg: Message):
    status = toggle_caption()
    await msg.reply(f"📝 Caption forwarding is now {'enabled' if status else 'disabled'}.")

@bot.on_message(filters.channel)
async def watermark_media(_, msg: Message):
    if str(msg.chat.id) not in get_allowed_channels():
        return

    wm_path = get_watermark()
    if not wm_path or not os.path.exists(wm_path):
        return

    cap = msg.caption if caption_enabled() else None

    if msg.photo:
        file_path = await msg.download()
        output = await add_watermark_to_image(file_path, wm_path)
        await bot.send_photo(chat_id=msg.chat.id, photo=output, caption=cap)
    elif msg.video:
        file_path = await msg.download()
        output = await add_watermark_to_video(file_path, wm_path)
        await bot.send_video(chat_id=msg.chat.id, video=output, caption=cap)

def get_allowed_channels():
    if os.path.exists("claimed.json"):
        with open("claimed.json") as f:
            return json.load(f)
    return []

bot.run()
