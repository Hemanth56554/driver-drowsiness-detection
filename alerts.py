import os
import requests
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_telegram(text):
    """Send a text message to your phone. Returns True if it worked."""
    if not TOKEN or not CHAT_ID:
        print("Telegram not set up: check TELEGRAM_TOKEN and TELEGRAM_CHAT_ID in .env")
        return False
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        reply = requests.post(url, data={"chat_id": CHAT_ID, "text": text}, timeout=10)
        return reply.ok
    except requests.RequestException as error:
        print("Telegram error:", error)
        return False


if __name__ == "__main__":
    ok = send_telegram("Test message from your drowsiness detector")
    print("Message sent" if ok else "Message failed")