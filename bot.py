import os
import logging
import asyncio
import aiohttp
from datetime import datetime, timezone, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)

BOT_TOKEN      = os.environ.get("8609914878:AAEaCwn65oa0J05U7VuUk-BqwM-FPVbSryY", "")
BOT_USERNAME   = "H_Anime_Hub777_Bot"
APP_URL        = "https://shibnathsarkar49-collab.github.io/Anime-World-/"
FIREBASE_KEY   = "AIzaSyCpnVJVXlNf2dE6p1Bw522Xh2n62bx5LVw"
PROJECT_ID     = "anime-world-7d366"
EARN_PER_REFER = 0.30

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not set!")

def get_day_key():
    ist = timezone(timedelta(hours=5, minutes=30))
    now = datetime.now(ist)
    return now.strftime("%Y-%m-%d")

async def credit_refer(ref_uid, by_uid):
    day_key = get_day_key()
    base = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents"
    key  = f"?key={FIREBASE_KEY}"

    async with aiohttp.ClientSession() as session:
        # Get current doc
        async with session.get(f"{base}/refers/{ref_uid}{key}") as r:
            doc = await r.json() if r.status == 200 else {}

        fields = doc.get("fields", {})

        # Check already credited today
        by_map   = fields.get("byUID", {}).get("mapValue", {}).get("fields", {})
        today_arr = [v["stringValue"] for v in by_map.get(day_key, {}).get("arrayValue", {}).get("values", [])]
        if by_uid in today_arr:
            return False

        today_arr.append(by_uid)

        # Current values
        def fval(key, typ="integerValue", default=0):
            v = fields.get(key, {})
            return float(v.get("doubleValue", v.get("integerValue", default)))

        new_fields = {
            "totalRefers":  {"integerValue": str(int(fval("totalRefers")) + 1)},
            "todayRefers":  {"integerValue": str(int(fval("todayRefers")) + 1)},
            "balance":      {"doubleValue":  round(fval("balance")     + EARN_PER_REFER, 2)},
            "totalEarned":  {"doubleValue":  round(fval("totalEarned") + EARN_PER_REFER, 2)},
            "todayEarned":  {"doubleValue":  round(fval("todayEarned") + EARN_PER_REFER, 2)},
            "byUID": {"mapValue": {"fields": {
                day_key: {"arrayValue": {"values": [{"stringValue": u} for u in today_arr]}}
            }}}
        }

        if fields:
            # Update existing
            masks = "&".join(f"updateMask.fieldPaths={f}" for f in new_fields)
            async with session.patch(f"{base}/refers/{ref_uid}{key}&{masks}", json={"fields": new_fields}) as r:
                return r.status in (200, 201)
        else:
            # Create new
            async with session.post(f"{base}/refers{key}&documentId={ref_uid}", json={"fields": new_fields}) as r:
                return r.status in (200, 201)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user      = update.effective_user
    by_uid    = f"tg_{user.id}"
    ref_param = context.args[0] if context.args else None

    if ref_param and ref_param.startswith("ref_"):
        ref_uid = ref_param[4:]
        if ref_uid != by_uid:
            await credit_refer(ref_uid, by_uid)

    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("🎌 Open H Anime Hub", web_app=WebAppInfo(url=APP_URL))
    ]])

    await update.message.reply_text(
        "🎌 H Anime Hub — এ স্বাগতম!\n\n"
        "🔥 Hindi Dubbed & Subbed Anime দেখো FREE তে\n"
        "💸 Daily Refer করো — ₹0.30 per refer উপার্জন করো\n"
        "🏆 1000 Refers = ₹300 সরাসরি তোমার Account এ!\n\n"
        "👇 নিচের বাটনে click করো Mini App খুলতে:",
        reply_markup=keyboard
    )

if __name__ == "__main__":
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("Bot starting...")
    asyncio.run(app.run_polling(drop_pending_updates=True))
