import requests
import time
from flask import Flask
import threading

WEBHOOK_URL = "https://discord.com/api/webhooks/1512845629938860242/cI1uxNg-J9TFNZJThRcJVg0AX6Y-I5SP4_V44OyzvPL0V6Rg_6MuasGmzQ_NFRWL5Ng3"

SEARCHES = [
    "ralph lauren",
    "polo ralph lauren",
    "ralph laurens",
    "ralph laren",
    "ralph laurn"
]

SEEN = set()
app = Flask(__name__)

def get_category(price):
    price = float(price)
    if price <= 10:
        return "🚨 URGENT"
    elif price <= 15:
        return "🟢 BARGAIN"
    else:
        return "🟡 POTENTIAL"

def send_discord(message):
    try:
        response = requests.post(WEBHOOK_URL, json={"content": message})
        print("Discord status:", response.status_code)
    except Exception as e:
        print("Webhook error:", e)

def fetch_items(search):
    url = "https://www.vinted.co.uk/api/v2/catalog/items"

    params = {
        "search_text": search,
        "price_to": 20,
        "order": "newest_first",
        "currency": "GBP",
        "per_page": 50
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)",
        "Accept": "application/json",
        "Accept-Language": "en-GB,en;q=0.9",
        "Referer": "https://www.vinted.co.uk/"
    }

    res = requests.get(url, params=params, headers=headers)

    print("Status:", res.status_code)

    try:
        data = res.json()
        print("Items returned:", len(data.get("items", [])))
        return data
    except:
        print("JSON parse failed")
        return {"items": []}

def is_valid(item):
    title = item["title"].lower()
    price = float(item["price"])

    if "ralph" not in title:
        return False

    if price > 20:
        return False

    return True

def format_item(item):
    title = item["title"]
    price = float(item["price"])
    size = item.get("size_title", "N/A")

    url = item.get("url", f"https://www.vinted.co.uk/items/{item['id']}")

    category = get_category(price)

    return f"""{category} Ralph Lauren Deal

👕 {title}
💰 £{price}
📏 Size: {size}

🔗 {url}
"""

def run_bot():
    while True:
        try:
            print("Checking for items...")

            # ✅ TEST MESSAGE EVERY LOOP
            send_discord("🔄 Bot running check...")

            for search in SEARCHES:
                data = fetch_items(search)

                for item in data.get("items", []):
                    item_id = item["id"]

                    if item_id not in SEEN and is_valid(item):
                        SEEN.add(item_id)

                        print("✅ Found:", item["title"])

                        send_discord(format_item(item))

            time.sleep(20)

        except Exception as e:
            print("Error:", e)
            time.sleep(60)

@app.route("/")
def home():
    # ✅ TEST WHEN YOU OPEN THE LINK
    send_discord("✅ Bot is LIVE (manual check)")
    return "Bot is running"

threading.Thread(target=run_bot).start()
app.run(host="0.0.0.0", port=10000)
