# -*- coding: utf-8 -*-
"""AR Code.Ai - بوت تيليجرام | © Ahmed Al-Obaidi (AR Code) | @ar.code.1"""
import os
import asyncio
import logging
import mimetypes

from google import genai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

from config import APP_NAME, DEVELOPER, INSTAGRAM, VERSION, get_api_key
from core import AREngine, MAX_BYTES

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
ALLOWED = {int(x) for x in os.getenv("TELEGRAM_ALLOWED_IDS", "").split(",") if x.strip().isdigit()}
CLIENT = None
ENGINES = {}


def engine_for(uid: int) -> AREngine:
    if uid not in ENGINES:
        ENGINES[uid] = AREngine(client=CLIENT)
    return ENGINES[uid]


def allowed(update: Update) -> bool:
    return not ALLOWED or update.effective_user.id in ALLOWED


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not allowed(update): return
    await update.message.reply_text(
        f"أهلاً! أني {APP_NAME} v{VERSION}\nتطوير: {DEVELOPER}\nانستغرام: @{INSTAGRAM}\n\n"
        "ارسل سؤال، صورة، PDF أو ملف كود، وراح أحللها.\n"
        "/clear مسح الذاكرة\n/search on|off البحث بالانترنت"
    )


async def clear(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not allowed(update): return
    engine_for(update.effective_user.id).reset()
    await update.message.reply_text("تم مسح الذاكرة ✅")


async def search_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not allowed(update): return
    on = not (ctx.args and ctx.args[0].lower() == "off")
    await asyncio.to_thread(engine_for(update.effective_user.id).set_search, on)
    await update.message.reply_text(f"البحث بالانترنت: {'مشغّل' if on else 'متوقف'}")


async def on_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not allowed(update): return
    msg = update.message
    text, files = msg.text or msg.caption or "", []
    try:
        if msg.photo:
            f = await msg.photo[-1].get_file()
            files.append(("photo.jpg", "image/jpeg", bytes(await f.download_as_bytearray())))
        elif msg.document:
            d = msg.document
            if d.file_size and d.file_size > MAX_BYTES:
                await msg.reply_text("الملف كبير جداً (الحد 18 ميغا)."); return
            f = await d.get_file()
            name = d.file_name or "file"
            mime = d.mime_type or mimetypes.guess_type(name)[0] or "application/octet-stream"
            files.append((name, mime, bytes(await f.download_as_bytearray())))
        elif msg.voice:
            f = await msg.voice.get_file()
            files.append(("voice.ogg", "audio/ogg", bytes(await f.download_as_bytearray())))
    except Exception as e:
        await msg.reply_text(f"⚠️ ما كدرت أحمّل الملف: {e}"); return

    await ctx.bot.send_chat_action(msg.chat_id, "typing")
    eng = engine_for(update.effective_user.id)
    try:
        answer = await asyncio.to_thread(eng.ask, text, files)
        answer += eng.sources_text()
    except Exception as e:
        answer = f"⚠️ خطأ: {e}"
    for i in range(0, len(answer), 4000):
        await msg.reply_text(answer[i:i + 4000])


def main():
    global CLIENT
    if not TOKEN:
        raise SystemExit("ضيف TELEGRAM_BOT_TOKEN بملف .env (من @BotFather)")
    CLIENT = genai.Client(api_key=get_api_key())
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(CommandHandler("search", search_cmd))
    app.add_handler(MessageHandler(
        (filters.TEXT & ~filters.COMMAND) | filters.PHOTO | filters.Document.ALL | filters.VOICE, on_message))
    print(f"{APP_NAME} Telegram bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
