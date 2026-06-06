import requests
import time

WEBHOOK_URL = "https://discord.com/api/webhooks/1512845629938860242/cI1uxNg-J9TFNZJThRcJVg0AX6Y-I5SP4_V44OyzvPL0V6Rg_6MuasGmzQ_NFRWL5Ng3"

SEARCH_TERMS = [
    "ralph lauren",
    "polo ralph lauren"
]

SEEN = set()

def send_discord(message):
    try:
        response = requests.post(WEBHOOK_URL, json={"content": message})
        print("Discord status:", response.status_code)
    except Exception as e:
        print("Discord error:", e)

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
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    params = {
        "search_text": search,
        "price_to": 20,
        "order": "newest_first",
        "per_page": 20
    }

    response = requests.get(url, headers=headers, params=params)

    print("Status:", response.status_code)

    if response.status_code != 200:
        return []

    try:
        data = response.json()
        return data.get("items", [])
    except:
        return []

def run_bot():
    print("🚀 Bot started")
    send_discord("✅ Bot is running!")

    while True:
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

                print("✅ Found:", title)

                msg = f"""{category} Ralph Lauren

👕 {title}
💰 £{price}

🔗 {url}
"""
                send_discord(msg)

        time.sleep(30)

run_bot()
