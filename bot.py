import os
import logging
import asyncio
from aiohttp import web
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)

BOT_TOKEN    = os.environ.get("8609914878:AAEaCwn65oa0J05U7VuUk-BqwM-FPVbSryY")
BOT_USERNAME = "H_Anime_Hub777_Bot"
APP_URL      = "https://shibnathsarkar49-collab.github.io/Anime-World-/"
PORT         = int(os.environ.get("PORT", 10000))

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not set!")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    ref  = args[0] if args else None
    url  = f"https://t.me/{BOT_USERNAME}/app?startapp={ref}" if (ref and ref.startswith("ref_")) else APP_URL
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("🎌 Open H Anime Hub", web_app=WebAppInfo(url=url))
    ]])
    text = (
        "🎌 H Anime Hub — এ স্বাগতম!\n\n"
        "🔥 Hindi Dubbed & Subbed Anime দেখো FREE তে\n"
        "💸 Daily Refer করো — ₹0.30 per refer উপার্জন করো\n"
        "🏆 1000 Refers = ₹300 সরাসরি তোমার Account এ!\n\n"
        "👇 নিচের বাটনে click করো Mini App খুলতে:"
    )
    await update.message.reply_text(text, reply_markup=keyboard)

async def health(request):
    return web.Response(text="OK")

async def main():
    # Build bot app
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))

    # Web server to keep Render happy (needs open port)
    runner = web.AppRunner(web.Application())
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

    print(f"Bot starting on port {PORT}...")

    # Start polling
    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)

    # Keep running forever
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
