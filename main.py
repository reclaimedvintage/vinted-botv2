import requests
import time
import re
from flask import Flask
import threading

WEBHOOK_URL = "https://discord.com/api/webhooks/1512845629938860242/cI1uxNg-J9TFNZJThRcJVg0AX6Y-I5SP4_V44OyzvPL0V6Rg_6MuasGmzQ_NFRWL5Ng3"

SEARCH_URLS = [
    "https://www.vinted.co.uk/catalog?search_text=ralph+lauren&price_to=20&order=newest_first"
]

SEEN = set()
app = Flask(__name__)

def send_discord(message):
    try:
        response = requests.post(WEBHOOK_URL, json={"content": message})
        print("Discord status:", response.status_code)
    except Exception as e:
        print("Webhook error:", e)

def get_category(price):
    price = float(price)
    if price <= 10:
        return "🚨 URGENT"
    elif price <= 15:
        return "🟢 BARGAIN"
    else:
        return "🟡 POTENTIAL"

def fetch_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)"
    }

    res = requests.get(url, headers=headers)
    return res.text

def extract_items(html):
    items = []

    # ✅ Extract item blocks
    matches = re.findall(r'href="(/items/\d+[^"]+)"[^>]*>.*?title="([^"]+)"', html)

    for match in matches:
        link = "https://www.vinted.co.uk" + match[0]
        title = match[1]

        # ✅ Try to find price nearby
        price_match = re.search(r'£(\d+)', html)
        price = float(price_match.group(1)) if price_match else 0

        if price <= 20:
            items.append({
                "id": link,
                "title": title,
                "price": price,
                "url": link
            })

    return items

def run_bot():
    print("🚀 BOT STARTED")

    send_discord("✅ Scraper bot started")

    while True:
        try:
            print("🔄 Checking site...")

            for url in SEARCH_URLS:
                html = fetch_page(url)

                items = extract_items(html)

                print(f"Items found: {len(items)}")

                for item in items:
                    if item["id"] not in SEEN:
                        SEEN.add(item["id"])

                        category = get_category(item["price"])

                        msg = f"""{category} Ralph Lauren Deal

👕 {item['title']}
💰 £{item['price']}

🔗 {item['url']}"""

                        print("✅ New item:", item["title"])

                        send_discord(msg)

            time.sleep(20)

        except Exception as e:
            print("Error:", e)
            time.sleep(60)

@app.route("/")
def home():
    return "Bot is running"

threading.Thread(target=run_bot).start()

app.run(host="0.0.0.0", port=10000)
