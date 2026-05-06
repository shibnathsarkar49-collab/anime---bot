import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)

BOT_TOKEN    = os.environ.get("BOT_TOKEN", "")
BOT_USERNAME = "H_Anime_Hub777_Bot"
APP_URL      = "https://shibnathsarkar49-collab.github.io/Anime-World-/"

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set!")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    ref  = args[0] if args else None

    if ref and ref.startswith("ref_"):
        url = f"https://t.me/{BOT_USERNAME}/app?startapp={ref}"
    else:
        url = APP_URL

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎌 Open H Anime Hub", web_app=WebAppInfo(url=url))]
    ])

    text = (
        "🎌 H Anime Hub — এ স্বাগতম!\n\n"
        "🔥 Hindi Dubbed & Subbed Anime দেখো FREE তে\n"
        "💸 Daily Refer করো — ₹0.30 per refer উপার্জন করো\n"
        "🏆 1000 Refers = ₹300 সরাসরি তোমার Account এ!\n\n"
        "👇 নিচের বাটনে click করো Mini App খুলতে:"
    )

    await update.message.reply_text(text, reply_markup=keyboard)

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("Bot starting...")
    app.run_polling()
