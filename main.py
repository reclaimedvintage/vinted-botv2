import requests
import time
from flask import Flask
import threading

WEBHOOK_URL = "https://discord.com/api/webhooks/1512845629938860242/cI1uxNg-J9TFNZJThRcJVg0AX6Y-I5SP4_V44OyzvPL0V6Rg_6MuasGmzQ_NFRWL5Ng3"

app = Flask(__name__)

def send_discord(message):
    try:
        response = requests.post(WEBHOOK_URL, json={"content": message})
        print("Discord status:", response.status_code)
    except Exception as e:
        print("Webhook error:", e)

def run_bot():
    print("🚀 BOT STARTED")

    # ✅ FORCE MESSAGE ON START
    send_discord("✅ BOT STARTED SUCCESSFULLY")

    while True:
        try:
            print("🔄 LOOP RUNNING")

            # ✅ FORCE MESSAGE EACH LOOP
            send_discord("🔄 Bot loop is running")

            time.sleep(20)

        except Exception as e:
            print("Error:", e)
            time.sleep(60)

@app.route("/")
def home():
    send_discord("🌐 Web request received")
    return "Bot is running"

# ✅ START THREAD PROPERLY
thread = threading.Thread(target=run_bot)
thread.daemon = True
thread.start()

app.run(host="0.0.0.0", port=10000)
