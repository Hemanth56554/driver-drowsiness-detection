import os
import threading
import requests
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def _send(text):
    """Runs in a background thread so the video never pauses."""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": text}, timeout=10)
    except requests.RequestException as error:
        print("Telegram error:", error)


def send_telegram(text):
    """Start sending a message and return immediately."""
    if not TOKEN or not CHAT_ID:
        print("Telegram not set up: check TELEGRAM_TOKEN and TELEGRAM_CHAT_ID in .env")
        return False
    threading.Thread(target=_send, args=(text,), daemon=True).start()
    return True


if __name__ == "__main__":
    send_telegram("Test message from your drowsiness detector")
    import time
    time.sleep(3)  # give the background thread time to finish
    print("Test message started")