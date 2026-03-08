import os
import time
import requests
from web3 import Web3

from utils import get_token_name, get_bnb_balance
from tg import send
from cex import CEX

RPC = os.getenv("RPC")
BSCSCAN_KEY = os.getenv("BSCSCAN_KEY")

ETHERSCAN = "https://api.etherscan.io/v2/api"
CHAIN_ID = 56

CREATOR = Web3.to_checksum_address("0x8480d0795615b535fb17392c24b42ea283b6f863")

w3 = Web3(Web3.HTTPProvider(RPC))

class Scanner:
    def __init__(self):
        self.last_block = w3.eth.block_number
        self.seen = set()
        self.funder_cache = {}

    def get_first_funder(self, addr):
        if addr in self.funder_cache:
            return self.funder_cache[addr]

        params = {
            "chainid": CHAIN_ID,
            "module": "account",
            "action": "txlist",
            "address": addr,
            "startblock": 0,
            "endblock": 99999999,
            "sort": "asc",
            "offset": 20,
            "apikey": BSCSCAN_KEY
        }

        try:
            r = requests.get(ETHERSCAN, params=params, timeout=10).json()
            if r.get("status") != "1" or not r.get("result"):
                return None

            for tx in r["result"]:
                if tx.get("to", "").lower() == addr.lower():
                    funder = tx["from"].lower()
                    self.funder_cache[addr] = funder
                    return funder
        except Exception as e:
            print(f"get_first_funder error: {e}")
        return None

    def trace_funding(self, dev):
        """追踪资金路径（最多4层，遇到CEX就停）"""
        path = []
        current = dev.lower()
        for _ in range(4):
            funder = self.get_first_funder(current)
            if not funder:
                break
            if funder in CEX:
                path.append(CEX[funder])
                break
            path.append(funder[:8] + "...")
            current = funder
        return " → ".join(path) if path else "未知"

    def scan(self):
        print("✅ Scanner 已启动，正在监控 Creator:", CREATOR)
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
