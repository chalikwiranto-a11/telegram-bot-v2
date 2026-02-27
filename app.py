from flask import Flask, request
import requests
import os
import logging
from telegram import Bot, Update

# Logging
logging.basicConfig(level=logging.INFO)

# Ambil environment variable
TOKEN = os.environ.get("TOKEN")
SHEET_API = os.environ.get("SHEET_API")

# Pastikan TOKEN dan SHEET_API ada
if not TOKEN:
    raise Exception("TOKEN tidak ditemukan di environment variables")

if not SHEET_API:
    raise Exception("SHEET_API tidak ditemukan di environment variables")

bot = Bot(token=TOKEN)
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running"

@app.route("/", methods=["POST"])
def webhook():
    try:
        data_json = request.get_json()

        if not data_json:
            return "ok"

        update = Update.de_json(data_json, bot)

        if update.message and update.message.text:
            serial = update.message.text.strip().upper()

            # =========================
            # REQUEST KE GOOGLE SHEETS
            # =========================
            try:
                res = requests.get(
                    f"{SHEET_API}?serial={serial}",
                    timeout=30
                )

                logging.info("STATUS CODE: %s", res.status_code)

                data = res.json()

            except Exception as e:
                logging.error("ERROR REQUEST SHEET: %s", str(e))

                bot.send_message(
                    chat_id=update.message.chat_id,
                    text="⚠️ Gagal konek ke database."
                )
                return "ok"

            # =========================
            # FORMAT BALASAN
            # =========================
            if data.get("found"):
                reply = f"""
🔎 DATA MATERIAL

Serial No : {data.get('serial','-')}
Shipment  : {data.get('shipment','-')}
Material  : {data.get('material','-')}
Vendor    : {data.get('vendor','-')}
Qty       : {data.get('qty','-')}
Year      : {data.get('receive_year','-')}
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
        logging.error("GENERAL ERROR: %s", str(e))

    return "ok"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
