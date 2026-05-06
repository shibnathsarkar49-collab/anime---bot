import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── CONFIG — তোমার নিজের values বসাও ──
BOT_TOKEN   = "8609914878:AAFcfu5h0effibclYh0CWqz2N6SWnKIPK20"
APP_NAME    = "app"           # BotFather এ Mini App এর short name যা দিয়েছ
BOT_USERNAME = "H_Anime_Hub777_Bot"
# ────────────────────────────────────────

MINI_APP_BASE = f"https://t.me/{BOT_USERNAME}/{APP_NAME}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /start command handler
    যখন user refer link click করে আসে:
      https://t.me/H_Anime_Hub777_Bot?start=ref_tg_12345
    Telegram bot কে পাঠায়: /start ref_tg_12345
    আমরা সেই param টা নিয়ে mini app link এ startapp= হিসেবে দিই
    """
    args = context.args  # /start এর পরের text
    ref_param = args[0] if args else None

    # Mini app URL — refer param থাকলে সেটা যোগ করো
    if ref_param and ref_param.startswith("ref_"):
        app_url = f"{MINI_APP_BASE}?startapp={ref_param}"
    else:
        app_url = MINI_APP_BASE

    # Welcome message
    welcome_text = (
        "🎌 *H Anime Hub — এ স্বাগতম!*\n\n"
        "🔥 Hindi Dubbed & Subbed Anime দেখো FREE তে\n"
        "🎬 Ads দেখো → Episodes Unlock করো\n"
        "💸 Daily Refer করো → ₹0.30 per refer উপার্জন করো\n"
        "🏆 1000 Refers = ₹300 সরাসরি তোমার Account এ!\n\n"
        "👇 নিচের বাটনে click করো Mini App খুলতে:"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "🎌 Open H Anime Hub",
            web_app=WebAppInfo(url=app_url)
        )]
    ])

    await update.message.reply_text(
        welcome_text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    logger.info("Bot starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
