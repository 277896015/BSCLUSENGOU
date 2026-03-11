import time
import os
from web3 import Web3
from utils import get_token_name, get_bnb_balance
from tg import send

# Telegram MarkdownV2 专用转义函数（核心修复！防止币名带 _ * . ! 等字符导致发送失败）
def escape_md2(text):
    """Telegram MarkdownV2 专用转义函数"""
    if not text:
        return ""
    text = str(text)
    chars = r'_*[]()~`>#+-=|{}.!'
    for char in chars:
        text = text.replace(char, '\\' + char)
    return text


RPC = os.getenv("RPC")
w3 = Web3(Web3.HTTPProvider(RPC))

CREATOR = Web3.to_checksum_address(
    "0x8480d0795615b535fb17392c24b42ea283b6f863"
)


class Scanner:

    def __init__(self):
        self.last_block = w3.eth.block_number
        self.seen = set()

    def scan(self):

        while True:

            try:

                latest = w3.eth.block_number

                logs = w3.eth.get_logs({
                    "fromBlock": self.last_block + 1,
                    "toBlock": latest,
                    "address": CREATOR
                })

                for log in logs:

                    # 防止 topics 不够导致崩溃
                    if len(log["topics"]) < 3:
                        continue

                    try:
                        dev = Web3.to_checksum_address(
                            "0x" + log["topics"][1].hex()[-40:]
                        )

                        token = Web3.to_checksum_address(
                            "0x" + log["topics"][2].hex()[-40:]
                        )

                    except Exception:
                        continue

                    if token in self.seen:
                        continue

                    self.seen.add(token)

                    name = get_token_name(w3, token)
                    bnb = get_bnb_balance(w3, dev)

                    # ←←← 关键修复：转义处理（名称和小数点必须转义）
                    name_esc = escape_md2(name)
                    bnb_esc = escape_md2(f"{bnb:.4f}")

                    msg = f"""
🚀 **新币上线**

**名称**: {name_esc}
**Token**: `{token}`
**Dev**: `{dev}`
**Dev BNB**: {bnb_esc} BNB
"""

                    send(msg)   # 默认使用 MarkdownV2，已在 tg.py 中配置好

                self.last_block = latest

            except Exception as e:
                print("scan error:", e)

            time.sleep(3)


if __name__ == "__main__":
    s = Scanner()
    s.scan()
