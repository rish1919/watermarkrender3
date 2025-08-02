from pyrogram import Client, filters
from pyrogram.types import Message
from watermark_utils import add_watermark_to_image, add_watermark_to_video
from utils import (
    is_owner, is_authorized_channel, set_watermark, get_watermark,
    delete_watermark, save_code, verify_code, load_code_data
)
import os

API_ID = int(os.environ.get("API_ID", "20712463"))
API_HASH = os.environ.get("API_HASH", "bee29238bf0db4a82548c2ffe29d43c1"))
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8413346186:AAFnzBn8rnj32W6XGpA5uXJI3EBhKCvwpg0"))
OWNER_ID = 7537050026

bot = Client("watermark-bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot.on_message(filters.command("start") & filters.private)
async def start(_, message: Message):
    await message.reply("👋 Welcome to the Watermark Bot!\n\nSend /claimcode <code> to activate the bot in your channel.")

@bot.on_message(filters.command("setwm") & filters.private)
async def setwm(_, message: Message):
    if not is_owner(message.from_user.id):
        return await message.reply("⛔ You're not authorized.")
    if not message.reply_to_message or not message.reply_to_message.photo:
        return await message.reply("📸 Reply to a PNG image to set as watermark.")
    watermark_file = f"watermarks/watermark.png"
    await message.reply_to_message.download(watermark_file)
    set_watermark(watermark_file)
    await message.reply("✅ Watermark set successfully.")

@bot.on_message(filters.command("showwm") & filters.private)
async def showwm(_, message: Message):
    if not is_owner(message.from_user.id):
        return await message.reply("⛔ You're not authorized.")
    wm = get_watermark()
    if not wm or not os.path.exists(wm):
        return await message.reply("❌ No watermark set.")
    await message.reply_photo(wm, caption="📌 Current watermark:")

@bot.on_message(filters.command("dltwm") & filters.private)
async def dltwm(_, message: Message):
    if not is_owner(message.from_user.id):
        return await message.reply("⛔ You're not authorized.")
    wm = get_watermark()
    if wm and os.path.exists(wm):
        os.remove(wm)
    delete_watermark()
    await message.reply("🗑️ Watermark deleted.")

@bot.on_message(filters.command("claimcode") & filters.private)
async def claim_code(_, message: Message):
    if len(message.command) < 2:
        return await message.reply("🔑 Use: /claimcode <code>")
    code = message.command[1]
    user_id = message.from_user.id
    success, msg = verify_code(code, user_id)
    await message.reply(msg)

@bot.on_message(filters.video | filters.photo & filters.channel)
async def auto_watermark(_, message: Message):
    if not is_authorized_channel(message.chat.id):
        return
    wm_path = get_watermark()
    if not wm_path or not os.path.exists(wm_path):
        return
    try:
        media = await message.download()
        output = None
        if message.photo:
            output = add_watermark_to_image(media, wm_path)
        elif message.video:
            output = await add_watermark_to_video(media, wm_path)
        if output:
            await message.reply_document(output, caption=message.caption or "💧 Watermarked")
            os.remove(output)
        os.remove(media)
    except Exception as e:
        print("Error:", e)

bot.run()
