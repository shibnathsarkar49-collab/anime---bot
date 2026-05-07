import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════
#   CONFIG — Railway Variables থেকে আসবে
# ═══════════════════════════════════════════════
BOT_TOKEN    = os.environ.get("BOT_TOKEN", "")
MINI_APP_URL = os.environ.get("MINI_APP_URL", "")   # https://yourusername.github.io/repo/
BOT_USERNAME = os.environ.get("BOT_USERNAME", "")   # H_Anime_Hub777_Bot (@ ছাড়া)

# ═══════════════════════════════════════════════
#   /start COMMAND
# ═══════════════════════════════════════════════
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user    = update.effective_user
    args    = context.args  # ["ref_tg_123456"] অথবা []
    name    = user.first_name or "বন্ধু"

    # ref param বের করো
    ref_param = ""
    if args and args[0].startswith("ref_"):
        ref_param = args[0]  # "ref_tg_123456"
        referrer_raw = ref_param[4:]  # "tg_123456"
        my_uid = f"tg_{user.id}"
        # self-refer block
        if referrer_raw == my_uid:
            ref_param = ""

    # Mini App URL তৈরি করো
    if ref_param:
        # start_param হিসেবে pass হবে → initDataUnsafe.start_param = "ref_tg_123456"
        app_url = f"https://t.me/{BOT_USERNAME}/{get_app_shortname()}?startapp={ref_param}"
        extra   = "\n👤 তুমি একজন বন্ধুর invite link দিয়ে এসেছ!\nMini App খুললেই তার wallet-এ ₹0.30 add হবে ✅"
    else:
        app_url = f"https://t.me/{BOT_USERNAME}/{get_app_shortname()}"
        extra   = ""

    text = (
        f"🎌 *H Anime Hub-এ স্বাগতম, {name}!*\n\n"
        f"✨ সেরা Anime দেখো — সম্পূর্ণ ফ্রি!\n\n"
        f"💸 *Refer করো & টাকা আয় করো!*\n"
        f"• প্রতি successful refer = ₹0.30\n"
        f"• ১,০০০ refer = ₹300 withdraw করো\n"
        f"• প্রতিদিন same friend থেকে আবার earn করো!"
        f"{extra}"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            text="🎌 Open H Anime Hub",
            web_app=WebAppInfo(url=app_url)
        )],
        [InlineKeyboardButton(
            text="📲 বন্ধুদের Invite করো & Earn করো",
            url=f"https://t.me/share/url?url=https://t.me/{BOT_USERNAME}?start=ref_tg_{user.id}&text=🎌 H Anime Hub-এ Anime দেখো %26 daily টাকা আয় করো!"
        )]
    ])

    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )

# ═══════════════════════════════════════════════
#   /refer COMMAND
# ═══════════════════════════════════════════════
async def refer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user     = update.effective_user
    ref_link = f"https://t.me/{BOT_USERNAME}?start=ref_tg_{user.id}"
    share    = f"https://t.me/share/url?url={ref_link}&text=🎌 আমার সাথে H Anime Hub দেখো %26 daily টাকা আয় করো!"

    text = (
        f"🎁 *তোমার Refer Link:*\n\n"
        f"`{ref_link}`\n\n"
        f"📋 *কীভাবে কাজ করে:*\n"
        f"1️⃣ বন্ধু link-এ click করে\n"
        f"2️⃣ Bot welcome message দেখায়\n"
        f"3️⃣ বন্ধু 'Open H Anime Hub' button tap করে\n"
        f"4️⃣ তোমার wallet-এ ₹0.30 instantly add ✅\n"
        f"5️⃣ রাত ১২টার পর reset → আবার earn করো!\n\n"
        f"💰 *Rate:* ₹0.30 per refer | ₹300 per 1,000"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📲 Telegram-এ Share করো", url=share)],
        [InlineKeyboardButton("🎌 Mini App খোলো", web_app=WebAppInfo(url=f"https://t.me/{BOT_USERNAME}/{get_app_shortname()}"))]
    ])

    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=keyboard)

# ═══════════════════════════════════════════════
#   /help COMMAND
# ═══════════════════════════════════════════════
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📋 *Commands:*\n\n"
        "/start — Bot শুরু করো\n"
        "/refer — তোমার refer link দেখো\n"
        "/help — সাহায্য\n\n"
        "🎌 Mini App-এ যাও Anime দেখতে ও refer track করতে!"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎌 Open H Anime Hub", web_app=WebAppInfo(url=f"https://t.me/{BOT_USERNAME}/{get_app_shortname()}"))]
    ])
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=keyboard)

# ═══════════════════════════════════════════════
#   HELPER — Mini App short name বের করো
# ═══════════════════════════════════════════════
def get_app_shortname():
    # MINI_APP_SHORTNAME env variable থেকে নেবে
    # যদি না থাকে তাহলে MINI_APP_URL থেকে guess করবে
    shortname = os.environ.get("MINI_APP_SHORTNAME", "")
    return shortname

# ═══════════════════════════════════════════════
#   MAIN
# ═══════════════════════════════════════════════
def main():
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN environment variable set করোনি!")
        return
    if not MINI_APP_URL:
        logger.error("❌ MINI_APP_URL environment variable set করোনি!")
        return
    if not BOT_USERNAME:
        logger.error("❌ BOT_USERNAME environment variable set করোনি!")
        return

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("refer", refer))
    app.add_handler(CommandHandler("help",  help_cmd))

    logger.info(f"✅ Bot @{BOT_USERNAME} starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
