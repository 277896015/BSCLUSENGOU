import os
from telegram import Bot

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=BOT_TOKEN)

def send(msg):

    try:
        bot.send_message(
            chat_id=CHAT_ID,
            text=msg,
            disable_web_page_preview=True
        )
    except Exception as e:
        print("TG error:", e)