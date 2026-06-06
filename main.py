import requests
import time
from flask import Flask
import threading

WEBHOOK_URL = "https://discord.com/api/webhooks/1512845629938860242/cI1uxNg-J9TFNZJThRcJVg0AX6Y-I5SP4_V44OyzvPL0V6Rg_6MuasGmzQ_NFRWL5Ng3"

SEARCH_TERMS = [
    "ralph lauren",
    "polo ralph lauren"
]

SEEN = set()
app = Flask(__name__)

def send_discord(message):
    try:
        response = requests.post(WEBHOOK_URL, json={"content": message})
        print("Discord:", response.status_code, flush=True)
    except Exception as e:
        print("Webhook error:", e, flush=True)

def get_category(price):
    price = float(price)
    if price <= 10:
        return "🚨 URGENT"
    elif price <= 15:
        return "🟢 BARGAIN"
    else:
        return "🟡 POTENTIAL"

def fetch_items(search):
    url = "https://www.vinted.co.uk/api/v2/catalog/items"

    params = {
        "search_text": search,
        "price_to": 20,
        "order": "newest_first",
        "per_page": 50,
        "currency": "GBP"
    }

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    r = requests.get(url, params=params, headers=headers)

    print("Status:", r.status_code, flush=True)

    try:
        data = r.json()
        print("Items returned:", len(data.get("items", [])), flush=True)
        return data.get("items", [])
    except:
        return []

def run_bot():
    print("🚀 BOT LOOP STARTED", flush=True)
    send_discord("✅ Bot started and running")

    while True:
        try:
            print("🔄 Checking Vinted...", flush=True)

            for term in SEARCH_TERMS:
                items = fetch_items(term)

                for item in items:
                    item_id = item["id"]
                    title = item["title"]
                    price = float(item["price"])

                    if item_id not in SEEN:
                        SEEN.add(item_id)

                        category = get_category(price)

                        url = item.get("url", f"https://www.vinted.co.uk/items/{item_id}")

                        print("✅ Sending:", title, flush=True)

                        msg = f"""{category} Ralph Lauren

👕 {title}
💰 £{price}

🔗 {url}
"""
                        send_discord(msg)

            time.sleep(20)

        except Exception as e:
            print("Error:", e, flush=True)
            time.sleep(60)

@app.route("/")
def home():
    return "Bot is running"

threading.Thread(target=run_bot, daemon=True).start()
app.run(host="0.0.0.0", port=10000)
