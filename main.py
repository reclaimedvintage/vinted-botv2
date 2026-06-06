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
    try:
        requests.post(WEBHOOK_URL, json={"content": message})
    except:
        print("Failed to send message")

def fetch_items(search):
    url = "https://www.vinted.co.uk/catalog?search_id=34787348416&page=1&time=1780765191"

    params = {
        "search_text": search,
        "price_to": 25,
        "order": "newest_first"
    }

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    res = requests.get(url, params=params, headers=headers)
    return res.json()

def is_valid(item):
    title = item["title"].lower()

    # ✅ Looser clothing filter
    keywords = [
        "shirt", "polo", "jumper", "sweater",
        "knit", "hoodie", "zip", "ralph"
    ]

    if not any(k in title for k in keywords):
        return False

    return True

def format_item(item):
    title = item["title"]
    price = float(item["price"])
    size = item.get("size_title", "N/A")
    url = f"https://www.vinted.co.uk/items/{item['id']}"

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
            for search in SEARCHES:
                data = fetch_items(search)

                for item in data.get("items", []):
                    item_id = item["id"]

                    if item_id not in SEEN and is_valid(item):
                        SEEN.add(item_id)
                        send_discord(format_item(item))

            time.sleep(25)

        except Exception as e:
            print("Error:", e)
            time.sleep(60)

@app.route("/")
def home():
    return "Bot is running"

threading.Thread(target=run_bot).start()

app.run(host="0.0.0.0", port=10000)
