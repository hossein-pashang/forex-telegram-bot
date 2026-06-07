import os
import hashlib
import requests
import feedparser
import schedule
import time
from datetime import datetime, timezone

# ========= تنظیمات =========

BOT_TOKEN = "8220464154:AAGM0pohheJTNbQi8X9p7tSIYUFWvzWDw4E"
CHAT_ID = "119580634"

BASE_DIR = "./data"
os.makedirs(BASE_DIR, exist_ok=True)

SEEN_FILE = os.path.join(BASE_DIR, "seen_hashes.txt")

if not os.path.exists(SEEN_FILE):
    open(SEEN_FILE, "w").close()

RSS_SOURCES = {
    "MYFXBOOK_NEWS": "https://www.myfxbook.com/rss/latest-forex-news",
    "FXSTREET_NEWS": "https://www.fxstreet.com/rss/news",
    "ORDER_FLOW": "https://investinglive.com/feed/forexorders/",
    "ECON_CALENDAR": "https://www.myfxbook.com/rss/forex-economic-calendar-events"
}

# ========= توابع =========

def send_telegram(text):
    try:
        rtl_text = "\u200F" + text

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

        payload = {
            "chat_id": CHAT_ID,
            "text": rtl_text[:4000]
        }

        requests.post(url, data=payload, timeout=30)

    except Exception as e:
        print("Telegram Error:", e)

def load_seen():
    with open(SEEN_FILE, "r", encoding="utf-8") as f:
        return set(x.strip() for x in f.readlines())

def save_seen(new_hashes):
    with open(SEEN_FILE, "a", encoding="utf-8") as f:
        for h in new_hashes:
            f.write(h + "\n")

def make_hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

# ========= RSS CHECK =========

def check_news():

    now = datetime.now(timezone.utc)

    print("Checking RSS:", now)

    seen = load_seen()
    new_hashes = set()

    total_new = 0

    for source, url in RSS_SOURCES.items():

        try:

            feed = feedparser.parse(url)

            for entry in feed.entries:

                title = entry.get("title", "").strip()
                link = entry.get("link", "").strip()

                content_key = f"{source}|{title}|{link}"

                h = make_hash(content_key)

                if h in seen:
                    continue

                new_hashes.add(h)

                msg = (
                    f"📢 {source}\n\n"
                    f"📰 {title}\n\n"
                    f"🔗 {link}"
                )

                send_telegram(msg)

                total_new += 1

                time.sleep(1)

        except Exception as e:
            print(f"RSS Error ({source}):", e)

    if new_hashes:
        save_seen(new_hashes)

    print(f"New articles sent: {total_new}")

# ========= START =========

send_telegram("✅ Forex News Bot Started")

check_news()

schedule.every(10).minutes.do(check_news)

while True:
    schedule.run_pending()
    time.sleep(5)
