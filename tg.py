import os
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"


def send(msg):

    try:

        requests.post(
            URL,
            json={
                "chat_id": CHAT_ID,
                "text": msg,
                "disable_web_page_preview": True
            },
            timeout=10
        )

    except Exception as e:

        print("TG error:", e)
