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

@app.route("/", methods=["POST"])
def webhook():
    data_json = request.get_json()

    if not data_json:
        return "ok"

    update = telegram.Update.de_json(data_json, bot)

    if update.message and update.message.text:
        serial = update.message.text.strip().upper()

        try:
            res = requests.get(f"{SHEET_API}?serial={serial}")
            data = res.json()
        except:
            bot.send_message(
                chat_id=update.message.chat_id,
                text="⚠️ Error koneksi ke database."
            )
            return "ok"

        if data.get("found"):
            reply = f"""
🔎 DATA MATERIAL

Serial No : {data['serial']}
Material  : {data.get('material','-')}
Vendor    : {data.get('vendor','-')}
Year      : {data.get('year','-')}
Identy    : {data.get('identy','-')}
Stock     : {data.get('stock','-')}
Location  : {data.get('location','-')}
Row       : {data.get('row','-')}
"""
        else:
            reply = "❌ Serial tidak ditemukan"

        bot.send_message(chat_id=update.message.chat_id, text=reply)

    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
