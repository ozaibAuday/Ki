import os
import requests
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
API = "https://api.alquran.cloud/v1"

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "السلام عليكم ✨\n"
        "أنا بوت القرآن الكريم.\n"
        "الأوامر:\n"
        "/surah رقم — لعرض سورة\n"
        "/ayah س:ع — لعرض آية\n"
        "/audio رقم — تشغيل السورة\n"
        "/list — عرض السور"
    )

# /list
async def list_surahs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    res = requests.get(f"{API}/surah").json()
    surahs = res["data"]
    txt = ""
    for s in surahs:
        txt += f"{s['number']}. {s['name']} — {s['englishName']} ({s['numberOfAyahs']} آية)\n"
    await update.message.reply_text(txt)

# /surah
async def surah(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        return await update.message.reply_text("اكتب: /surah 1")

    number = args[0]

    res = requests.get(f"{API}/surah/{number}/quran-uthmani").json()

    if res["status"] != "OK":
        return await update.message.reply_text("لم أجد السورة.")

    data = res["data"]
    name = data["name"]
    ayahs = data["ayahs"]

    await update.message.reply_text(f"سورة {name} — عدد الآيات: {len(ayahs)}")

    # إرسال الآيات على دفعات
    chunk = ""
    count = 0
    for a in ayahs:
        chunk += f"{a['numberInSurah']}. {a['text']}\n\n"
        count += 1
        if count == 10:
            await update.message.reply_text(chunk)
            chunk = ""
            count = 0

    if chunk:
        await update.message.reply_text(chunk)

    # زر الصوت
    audio_url = f"https://api.alquran.cloud/v1/surah/{number}/ar.alafasy"
    button = InlineKeyboardButton("استمع للسورة 🎧", url=audio_url)
    await update.message.reply_text("الصوت:", reply_markup=InlineKeyboardMarkup([[button]]))

# /ayah
async def ayah(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("اكتب: /ayah 2:255")

    ref = context.args[0]

    res = requests.get(f"{API}/ayah/{ref}/quran-uthmani").json()

    if res["status"] != "OK":
        return await update.message.reply_text("لم أجد الآية.")

    data = res["data"]
    await update.message.reply_text(f"{ref}\n\n{data['text']}")

    # صوت الآية
    audio_res = requests.get(f"{API}/ayah/{ref}/ar.alafasy").json()
    audio = audio_res["data"].get("audio")

    if audio:
        await update.message.reply_audio(audio, caption=f"صوت الآية {ref}")

# /audio
async def audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("استخدم: /audio 1")

    number = context.args[0]

    res = requests.get(f"{API}/surah/{number}/ar.alafasy").json()

    if "data" in res and "audio" in res["data"]:
        return await update.message.reply_audio(res["data"]["audio"], caption=f"سورة رقم {number}")

    url = f"https://api.alquran.cloud/v1/surah/{number}/ar.alafasy"
    button = InlineKeyboardButton("استمع للسورة 🎧", url=url)
    await update.message.reply_text("الصوت:", reply_markup=InlineKeyboardMarkup([[button]]))


async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("list", list_surahs))
    app.add_handler(CommandHandler("surah", surah))
    app.add_handler(CommandHandler("ayah", ayah))
    app.add_handler(CommandHandler("audio", audio))

    print("Bot Started…")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
