import os
import requests

# 从环境变量获取配置（和你Railway里的变量名一致）
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send(content):
    """TG消息发送函数，供scanner.py调用"""
    # 校验参数
    if not BOT_TOKEN or not CHAT_ID:
        print("错误：BOT_TOKEN或CHAT_ID未配置")
        return False
    
    # 使用TG反向代理（解决Railway访问TG API的问题）
    url = f"https://tgapi.qqsuu.cn/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": content,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"TG发送响应：{response.status_code} | {response.text}")
        if response.status_code == 200:
            print("TG消息发送成功")
            return True
        else:
            print(f"TG发送失败：{response.text}")
            return False
    except Exception as e:
        print(f"TG发送异常：{str(e)}")
        return False
