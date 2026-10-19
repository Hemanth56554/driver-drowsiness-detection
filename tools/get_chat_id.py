import os
import requests
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("TELEGRAM_TOKEN")

if not token:
    print("Token not found. Check that .env has the line TELEGRAM_TOKEN=...")
else:
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    data = requests.get(url, timeout=10).json()
    if not data.get("ok"):
        print("Telegram rejected the token. Check the token in .env")
    elif not data["result"]:
        print("No messages found. Send 'hello' to your bot on your phone, then run this again.")
    else:
        chat = data["result"][-1]["message"]["chat"]
        print("Your chat ID is:", chat["id"])
        print("Name:", chat.get("first_name", ""))