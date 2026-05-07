import os
import logging
import asyncio
import aiohttp
from datetime import datetime, timezone, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)

BOT_TOKEN      = os.environ.get("BOT_TOKEN", "")
BOT_USERNAME   = "H_Anime_Hub777_Bot"
APP_URL        = "https://shibnathsarkar49-collab.github.io/Anime-World-/"
FIREBASE_KEY   = "AIzaSyCpnVJVXlNf2dE6p1Bw522Xh2n62bx5LVw"
PROJECT_ID     = "anime-world-7d366"
EARN_PER_REFER = 0.30

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not set!")

def get_day_key():
    # IST = UTC+5:30
    ist = timezone(timedelta(hours=5, minutes=30))
    now = datetime.now(ist)
    return now.strftime("%Y-%m-%d")

def firestore_url(doc_path):
    return f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/{doc_path}?key={FIREBASE_KEY}"

async def get_refer_doc(session, ref_uid):
    url = firestore_url(f"refers/{ref_uid}")
    async with session.get(url) as r:
        if r.status == 200:
            return await r.json()
        return None

async def credit_refer(ref_uid, by_uid):
    day_key = get_day_key()
    async with aiohttp.ClientSession() as session:
        # Get current refer doc
        doc = await get_refer_doc(session, ref_uid)
        
        if doc and "fields" in doc:
            fields = doc["fields"]
            # Check already credited today by this user
            by_arr = []
            if "byUID" in fields:
                day_data = fields["byUID"].get("mapValue", {}).get("fields", {})
                if day_key in day_data:
                    by_arr = [v["stringValue"] for v in day_data[day_key].get("arrayValue", {}).get("values", [])]
            
            if by_uid in by_arr:
                return False  # Already credited today
            
            # Get current values
            cur_count  = int(fields.get("totalRefers", {}).get("integerValue", 0))
            cur_today  = int(fields.get("todayRefers", {}).get("integerValue", 0))
            cur_bal    = float(fields.get("balance", {}).get("doubleValue", 0) or fields.get("balance", {}).get("integerValue", 0))
            cur_earned = float(fields.get("totalEarned", {}).get("doubleValue", 0) or fields.get("totalEarned", {}).get("integerValue", 0))
            cur_day_earn = float(fields.get("todayEarned", {}).get("doubleValue", 0) or fields.get("todayEarned", {}).get("integerValue", 0))
            
            # Add by_uid to today's array
            by_arr.append(by_uid)
            
            # Build updated doc
            new_fields = {
                "totalRefers":  {"integerValue": str(cur_count + 1)},
                "todayRefers":  {"integerValue": str(cur_today + 1)},
                "balance":      {"doubleValue": round(cur_bal + EARN_PER_REFER, 2)},
                "totalEarned":  {"doubleValue": round(cur_earned + EARN_PER_REFER, 2)},
                "todayEarned":  {"doubleValue": round(cur_day_earn + EARN_PER_REFER, 2)},
                "byUID": {
                    "mapValue": {
                        "fields": {
                            day_key: {
                                "arrayValue": {
                                    "values": [{"stringValue": u} for u in by_arr]
                                }
                            }
                        }
                    }
                }
            }
            
            # Patch the document
            patch_url = firestore_url(f"refers/{ref_uid}") + "&updateMask.fieldPaths=totalRefers&updateMask.fieldPaths=todayRefers&updateMask.fieldPaths=balance&updateMask.fieldPaths=totalEarned&updateMask.fieldPaths=todayEarned&updateMask.fieldPaths=byUID"
            async with session.patch(patch_url.replace("?key=", "?key="), json={"fields": new_fields}) as r:
                return r.status in (200, 201)
        else:
            # Create new refer doc
            new_fields = {
                "totalRefers":  {"integerValue": "1"},
                "todayRefers":  {"integerValue": "1"},
                "balance":      {"doubleValue": EARN_PER_REFER},
                "totalEarned":  {"doubleValue": EARN_PER_REFER},
                "todayEarned":  {"doubleValue": EARN_PER_REFER},
                "byUID": {
                    "mapValue": {
                        "fields": {
                            day_key: {
                                "arrayValue": {
                                    "values": [{"stringValue": by_uid}]
                                }
                            }
                        }
                    }
                }
            }
            url = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/refers?documentId={ref_uid}&key={FIREBASE_KEY}"
            async with session.post(url, json={"fields": new_fields}) as r:
                return r.status in (200, 201)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    by_uid = f"tg_{user.id}"
    args = context.args
    ref_param = args[0] if args else None

    credited = False
    if ref_param and ref_param.startswith("ref_"):
        ref_uid = ref_param[4:]  # remove "ref_" prefix
        if ref_uid != by_uid:   # block self-refer
            credited = await credit_refer(ref_uid, by_uid)

    url = f"https://t.me/{BOT_USERNAME}/app?startapp={ref_param}" if ref_param else APP_URL

    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("🎌 Open H Anime Hub", web_app=WebAppInfo(url=APP_URL))
    ]])

    text = (
        "🎌 H Anime Hub — এ স্বাগতম!\n\n"
        "🔥 Hindi Dubbed & Subbed Anime দেখো FREE তে\n"
        "💸 Daily Refer করো — ₹0.30 per refer উপার্জন করো\n"
        "🏆 1000 Refers = ₹300 সরাসরি তোমার Account এ!\n\n"
        "👇 নিচের বাটনে click করো Mini App খুলতে:"
    )

    await update.message.reply_text(text, reply_markup=keyboard)

async def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("Bot starting...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling(drop_pending_updates=True)
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
