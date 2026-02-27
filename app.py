from flask import Flask, request
import requests
import os
import telegram

TOKEN = os.environ.get("TOKEN")
SHEET_API = os.environ.get("SHEET_API")

bot = telegram.Bot(token=TOKEN)
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running"

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    if update.message:
        serial = update.message.text.strip().upper()

        res = requests.get(f"{SHEET_API}?serial={serial}")
        data = res.json()

        if data.get("found"):
            reply = f"""
🔎 DATA MATERIAL

Serial No : {data['serial']}
Material  : {data['material']}
Vendor    : {data['vendor']}
Year      : {data['year']}
Identy    : {data['identy']}
Stock     : {data['stock']}
Location  : {data['location']}
Row       : {data['row']}
"""
        else:
            reply = "❌ Serial tidak ditemukan"

        bot.send_message(chat_id=update.message.chat_id, text=reply)

    return "ok"