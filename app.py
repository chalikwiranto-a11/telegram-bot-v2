from flask import Flask, request
import requests
import os
import telegram
import logging

# Logging agar error terlihat di Railway
logging.basicConfig(level=logging.INFO)

TOKEN = os.environ.get("TOKEN")
SHEET_API = os.environ.get("SHEET_API")

bot = telegram.Bot(token=TOKEN)
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running"

@app.route("/", methods=["POST"])
def webhook():
    try:
        data_json = request.get_json(force=True)

        if not data_json:
            return "ok"

        update = telegram.Update.de_json(data_json, bot)

        if update.message and update.message.text:
            serial = update.message.text.strip().upper()

            # Request ke Google Apps Script
            res = requests.get(
                f"{SHEET_API}?serial={serial}",
                timeout=15
            )

            logging.info("STATUS CODE: %s", res.status_code)
            logging.info("RESPONSE TEXT: %s", res.text)

            # Pastikan response valid JSON
            data = res.json()

            if data.get("found"):
                reply = f"""
🔎 DATA MATERIAL

Serial No : {data.get('serial','-')}
Material  : {data.get('material','-')}
Vendor    : {data.get('vendor','-')}
Year      : {data.get('receive_year','-')}
Stock     : {data.get('qty','-')}
Location  : {data.get('location','-')}
Row       : {data.get('row','-')}
"""
            else:
                reply = "❌ Serial tidak ditemukan"

            bot.send_message(
                chat_id=update.message.chat_id,
                text=reply
            )

    except Exception as e:
        logging.error("ERROR: %s", str(e))

    return "ok"


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
