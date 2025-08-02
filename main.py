import os
import json
import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from watermark_utils import add_watermark_to_image, add_watermark_to_video
from utils import is_owner, get_watermark_path, caption_enabled, toggle_caption, save_watermark
from claim_utils import validate_code

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")

bot = Client("watermark_bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

@bot.on_message(filters.command("start"))
async def start_handler(client, message: Message):
    await message.reply_text("👋 Welcome to the Watermark Bot!\nSend /setwm to upload your watermark PNG.\nUse /claimcode CODE to activate the bot in your channel.")

@bot.on_message(filters.command("setwm") & filters.private & is_owner)
async def set_watermark_handler(client, message: Message):
    if message.reply_to_message and message.reply_to_message.document:
        file = await message.reply_to_message.download()
        save_watermark(file)
        await message.reply("✅ Watermark saved successfully.")
    else:
        await message.reply("⚠️ Reply to a PNG file with /setwm.")

@bot.on_message(filters.command("showwm") & filters.private & is_owner)
async def show_watermark(client, message: Message):
    path = get_watermark_path()
    if os.path.exists(path):
        await message.reply_photo(photo=path, caption="🖼 Current watermark")
    else:
        await message.reply("⚠️ No watermark is set.")

@bot.on_message(filters.command("dltwm") & filters.private & is_owner)
async def delete_watermark(client, message: Message):
    path = get_watermark_path()
    if os.path.exists(path):
        os.remove(path)
        await message.reply("🗑 Watermark deleted.")
    else:
        await message.reply("⚠️ No watermark to delete.")

@bot.on_message(filters.command("caption") & filters.private & is_owner)
async def toggle_caption_handler(client, message: Message):
    args = message.text.split()
    if len(args) != 2 or args[1].lower() not in ["on", "off"]:
        await message.reply("Usage: /caption on or /caption off")
        return
    toggle_caption(args[1].lower() == "on")
    await message.reply(f"✅ Caption turned {args[1].lower()}.")

@bot.on_message(filters.command("claimcode") & filters.private)
async def claim_code_handler(client, message: Message):
    args = message.text.split()
    if len(args) != 2:
        await message.reply("❌ Usage: /claimcode YOUR_CODE")
        return
    code = args[1].strip().upper()
    chat_id = message.chat.id
    success = validate_code(code, chat_id)
    if success:
        await message.reply("✅ Code claimed! Watermarking activated in your channel.")
    else:
        await message.reply("❌ Invalid or already used code.")

@bot.on_message(filters.channel)
async def watermark_channel_post(client, message: Message):
    chat_id = message.chat.id
    with open("claimed.json", "r") as f:
        claimed = json.load(f)
    if str(chat_id) not in claimed:
        return

    path = get_watermark_path()
    if not os.path.exists(path):
        return

    try:
        if message.photo:
            output = add_watermark_to_image(message)
            await client.send_photo(chat_id, photo=output, caption=message.caption if caption_enabled() else None)
        elif message.video:
            output = await add_watermark_to_video(message)
            await client.send_video(chat_id, video=output, caption=message.caption if caption_enabled() else None)
    except Exception as e:
        logger.error(f"❌ Error processing message: {e}")

if __name__ == "__main__":
    bot.run()
