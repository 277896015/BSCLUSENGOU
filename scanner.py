import os
import time
import requests
from web3 import Web3

from utils import get_token_name, get_bnb_balance
from tg import send
from cex import CEX

RPC = os.getenv("RPC")
BSCSCAN_KEY = os.getenv("BSCSCAN_KEY")  # 暂时不用了，可留空

CREATOR = Web3.to_checksum_address("0x8480d0795615b535fb17392c24b42ea283b6f863")

w3 = Web3(Web3.HTTPProvider(RPC))

class Scanner:
    def __init__(self):
        self.last_block = w3.eth.block_number
        self.seen = set()

    def trace_funding(self, dev):
        """临时关闭资金路径追踪（API已停用）"""
        return "未知 (BSC API暂停使用，待升级)"

    def scan(self):
        print("✅ Scanner 已启动（简化版），正在监控 Creator:", CREATOR)
        while True:
            try:
                latest = w3.eth.block_number
                if latest <= self.last_block:
                    time.sleep(2)
                    continue

                logs = w3.eth.get_logs({
                    "fromBlock": self.last_block + 1,
                    "toBlock": latest,
                    "address": CREATOR
                })

                for log in logs:
                    token = Web3.to_checksum_address(log["address"])
                    if token in self.seen:
                        continue
                    self.seen.add(token)

                    dev = Web3.to_checksum_address(log["topics"][1][-20:].hex())

                    name = get_token_name(w3, token)
                    bnb = get_bnb_balance(w3, dev)
                    path = self.trace_funding(dev)

                    msg = f"""
🚀 **新币上线**

**名称**: {name}
**Token**: `{token}`
**Dev**: `{dev}`
**Dev BNB**: {bnb:.4f} BNB
**资金路径**: {path}
                    """

                    send(msg)
                    print(f"[+] 发现新币: {name} | {token}")

                self.last_block = latest
            except Exception as e:
                print("scan error:", e)

            time.sleep(2)


if __name__ == "__main__":
    scanner = Scanner()
    scanner.scan()
