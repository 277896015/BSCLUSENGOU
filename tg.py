import os
import requests

# 从环境变量读取配置（和你Railway的变量名保持一致）
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# 改回官方TG API地址（核心修复点）
URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

def send(msg):
    """发送TG消息，保留原有逻辑+增加详细日志排查问题"""
    # 先校验参数是否为空
    if not BOT_TOKEN or not CHAT_ID:
        print("TG error: BOT_TOKEN或CHAT_ID未配置")
        return
    
    try:
        # 发送请求（保留你原有参数：disable_web_page_preview=True）
        response = requests.post(
            URL,
            json={
                "chat_id": CHAT_ID,
                "text": msg,
                "disable_web_page_preview": True  # 保留你原有配置
            },
            timeout=10
        )
        # 增加日志：打印响应状态和内容，方便排查
        print(f"TG响应状态码: {response.status_code}")
        print(f"TG响应内容: {response.text}")
        if response.status_code == 200:
            print("TG消息发送成功")
        else:
            print(f"TG发送失败: {response.text}")
            
    except Exception as e:
        print(f"TG error: {e}")
        # 备选方案：若官方地址仍访问失败，自动切换备用代理（可选）
        try:
            backup_url = f"https://api.telegram.dog/bot{BOT_TOKEN}/sendMessage"
            response = requests.post(
                backup_url,
                json={"chat_id": CHAT_ID, "text": msg, "disable_web_page_preview": True},
                timeout=10
            )
            print(f"备用代理响应: {response.status_code} | {response.text}")
        except Exception as backup_e:
            print(f"备用代理也失败: {backup_e}")
