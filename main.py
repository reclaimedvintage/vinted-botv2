import requests
import time
from flask import Flask
import threading

WEBHOOK_URL = "https://discord.com/api/webhooks/1512845629938860242/cI1uxNg-J9TFNZJThRcJVg0AX6Y-I5SP4_V44OyzvPL0V6Rg_6MuasGmzQ_NFRWL5Ng3"

SEARCHES = [
    "ralph lauren",
    "polo ralph lauren",
    "ralph lauren shirt",
    "ralph lauren polo",
    "ralph lauren jumper",
    "ralph lauren sweater",
    "ralph lauren knitwear",
    "ralph lauren vintage",
    "ralph laurens",
    "ralph laurn",
    "ralph laren"
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
    requests.post(WEBHOOK_URL, json={"content": message})

def fetch_items(search):
    url = "https://www.vinted.co.uk/api/v2/catalog/items"
    
    params = {
        "search_text": search,
        "price_to": 25,
        "catalog_ids": 5,
        "order": "newest_first"
    }

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    res = requests.get(url, params=params, headers=headers)
    return res.json()

def is_valid(item):
    title = item["title"].lower()
    condition = item["status"]

    # ✅ Condition filter
    if condition not in [
        "very_good",
        "new_with_tags",
        "new_without_tags"
    ]:
        return False

    # ✅ Clothing filter
    keywords = ["shirt", "polo", "jumper", "sweater", "knit"]


def format_item(item):
    title = item["title"]
    price = float(item["price"])
    size = item.get("size_title", "N/A")
    condition = item["status"]

    condition_map = {
        "very_good": "Very Good",
        "new_with_tags": "New with tags",
        "new_without_tags": "New without tags"
    }

    condition = condition_map.get(condition, condition)

    url = f"https://www.vinted.co.uk/items/{item['id']}"
    category = get_category(price)

    return f"""{category} Ralph Lauren Deal

👕 {title}
💰 £{price}
📏 Size: {size}
✅ Condition: {condition}

🔗 {url}
"""

def run_bot():
    while True:
        try:
            for search in SEARCHES:
                data = fetch_items(search)

                for item in data["items"]:
                    item_id = item["id"]

                    if item_id not in SEEN and is_valid(item):
                        SEEN.add(item_id)
                        send_discord(format_item(item))

            time.sleep(30)

        except Exception as e:
            print(e)
            time.sleep(60)

@app.route("/")
def home():
    send_discord("✅ Test message from bot")
    return "Bot is running"

# run bot in background
threading.Thread(target=run_bot).start()

# run web server
app.run(host="0.0.0.0", port=10000)
