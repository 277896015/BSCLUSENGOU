import os
import requests

# 从环境变量读取配置
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

def send(msg, parse_mode="MarkdownV2"):
    """发送TG消息，支持MarkdownV2（默认启用）"""
    if not BOT_TOKEN or not CHAT_ID:
        print("TG error: BOT_TOKEN或CHAT_ID未配置")
        return
    
    try:
        response = requests.post(
            URL,
            json={
                "chat_id": CHAT_ID,
                "text": msg,
                "disable_web_page_preview": True,
                "parse_mode": parse_mode          # ←←← 关键一行！启用Markdown
            },
            timeout=10
        )
        print(f"TG响应状态码: {response.status_code}")
        print(f"TG响应内容: {response.text}")
        if response.status_code == 200:
            print("TG消息发送成功 ✅")
        else:
            print(f"TG发送失败: {response.text}")
            
    except Exception as e:
        print(f"TG error: {e}")
        # 备用代理（也加上parse_mode）
        try:
            backup_url = f"https://api.telegram.dog/bot{BOT_TOKEN}/sendMessage"
            response = requests.post(
                backup_url,
                json={
                    "chat_id": CHAT_ID,
                    "text": msg,
                    "disable_web_page_preview": True,
                    "parse_mode": parse_mode      # ←←← 备用也加上
                },
                timeout=10
            )
            print(f"备用代理响应: {response.status_code} | {response.text}")
        except Exception as backup_e:
            print(f"备用代理也失败: {backup_e}")
