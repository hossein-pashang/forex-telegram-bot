import os
import hashlib
import requests
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime, timezone

# ========= تنظیمات =========
# برای تست موقت، توکن و Chat ID را مستقیم اینجا می‌گذاریم
BOT_TOKEN ="8220464154:AAEtuHy4wRaWCJlaZMU5Ts2B-yOzmPrAcEI"
CHAT_ID ="119580634"                           # Chat ID تو

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
    # اضافه کردن کاراکتر راست‌چین برای فارسی
    rtl_text = "\u200F" + text
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": rtl_text[:4000]
    }
    requests.post(url, data=payload)

def load_seen():
    with open(SEEN_FILE, "r") as f:
        return set(x.strip() for x in f.readlines())

def save_seen(new_hashes):
    with open(SEEN_FILE, "a") as f:
        for h in new_hashes:
            f.write(h + "\n")

def make_hash(text):
    return hashlib.sha256(text.encode()).hexdigest()

# ========= بخش اصلی =========

def run():
    # پیام تست مستقیم
    send_telegram("✅ ربات با موفقیت اجرا شد و تست پیام رسید!")

    # این بخش RSS فعلی
    now = datetime.now(timezone.utc)
    seen = load_seen()
    new_hashes = set()
    messages = []

    for source, url in RSS_SOURCES.items():
        feed = feedparser.parse(url)

        for entry in feed.entries:
            title = entry.get("title", "").strip()
            link = entry.get("link", "").strip()

            content_key = f"{source}|{title}|{link}"
            h = make_hash(content_key)

            if h in seen:
                continue

            new_hashes.add(h)

            msg = f"📢 {source}\n📰 عنوان: {title}\n🔗 لینک: {link}"
            messages.append(msg)

    if messages:
        for m in messages:
            send_telegram(m)
        save_seen(new_hashes)

if __name__ == "__main__":
    run()

