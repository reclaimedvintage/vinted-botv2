import requests
import time
import random
from flask import Flask
import threading

WEBHOOK_URL = "https://discord.com/api/webhooks/1512845629938860242/cI1uxNg-J9TFNZJThRcJVg0AX6Y-I5SP4_V44OyzvPL0V6Rg_6MuasGmzQ_NFRWL5Ng3"

SEARCH_TERMS = [
    "ralph lauren",
    "polo ralph lauren"
]

SEEN = set()
app = Flask(__name__)

# ✅ Create persistent session (IMPORTANT)
session = requests.Session()

# ✅ Realistic headers (rotating)
USER_AGENTS = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
]

def send_discord(message):
    try:
        response = requests.post(WEBHOOK_URL, json={"content": message})
        print("Discord:", response.status_code, flush=True)
    except Exception as e:
        print("Discord error:", e, flush=True)

def get_category(price):
    if price <= 10:
        return "🚨 URGENT"
    elif price <= 15:
        return "🟢 BARGAIN"
    else:
        return "🟡 POTENTIAL"

def fetch_items(search):
    url = "https://www.vinted.co.uk/api/v2/catalog/items"

    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "application/json",
        "Accept-Language": "en-GB,en;q=0.9",
        "Referer": "https://www.vinted.co.uk/",
        "Origin": "https://www.vinted.co.uk",
        "Connection": "keep-alive"
    }

    params = {
        "search_text": search,
        "price_to": 20,
        "order": "newest_first",
        "per_page": 20,
        "currency": "GBP"
    }

    try:
        response = session.get(url, headers=headers, params=params, timeout=10)

        print("Status:", response.status_code, flush=True)

        if response.status_code != 200:
            return []

        data = response.json()
        items = data.get("items", [])

        print("Items returned:", len(items), flush=True)
        return items

    except Exception as e:
        print("Fetch error:", e, flush=True)
        return []

def run_bot():
    print("🚀 BOT STARTED", flush=True)
    send_discord("✅ Bot started (stealth mode)")

    while True:
        try:
            print("🔄 Checking Vinted...", flush=True)

            for term in SEARCH_TERMS:
                items = fetch_items(term)

                for item in items:
                    item_id = item["id"]
                    title = item["title"]
                    price = float(item["price"])

                    if item_id in SEEN:
                        continue

                    SEEN.add(item_id)

                    category = get_category(price)

                    url = item.get("url", f"https://www.vinted.co.uk/items/{item_id}")

                    print("✅ Found:", title, flush=True)

                    msg = f"""{category} Ralph Lauren

👕 {title}
💰 £{price}

🔗 {url}
"""

                    send_discord(msg)

            # ✅ RANDOM DELAY (CRITICAL)
            sleep_time = random.randint(25, 40)
            print(f"⏳ Sleeping {sleep_time}s...", flush=True)
            time.sleep(sleep_time)

        except Exception as e:
            print("Error:", e, flush=True)
            time.sleep(60)

@app.route("/")
def home():
    return "Bot is running"

threading.Thread(target=run_bot, daemon=True).start()
app.run(host="0.0.0.0", port=10000)
