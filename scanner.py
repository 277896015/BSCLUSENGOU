import requests
import time
import os
from web3 import Web3
from utils import get_token_name, get_bnb_balance
from tg import send

CREATOR = Web3.to_checksum_address(
    "0x8480d0795615b535fb17392c24b42ea283b6f863"
)
BSCSCAN_KEY = os.getenv("BSCSCAN_KEY")
CREATOR_ABI = [
{
"anonymous": False,
"inputs": [
{"indexed": True, "name": "owner", "type": "address"},
{"indexed": True, "name": "token", "type": "address"},
{"indexed": False, "name": "tokenType", "type": "uint8"},
{"indexed": False, "name": "version", "type": "uint256"}
],
"name": "TokenCreated",
"type": "event"
}
]

TRANSFER_TOPIC = Web3.keccak(
    text="Transfer(address,address,uint256)"
).hex()

class Scanner:

    def __init__(self, w3):

        self.w3 = w3

        self.contract = w3.eth.contract(
            address=CREATOR,
            abi=CREATOR_ABI
        )

        self.seen = set()

    def get_first_funder(self, dev):

      try:

          url = "https://api.bscscan.com/api"

          params = {
                 "module": "account",
                 "action": "txlist",
                 "address": dev,
                 "startblock": 0,
                 "endblock": 99999999,
                 "sort": "asc",
                 "offset": 10,
                 "apikey": BSCSCAN_KEY
           }

          r = requests.get(url, params=params, timeout=10).json()

          txs = r.get("result", [])

          if not txs:
            return "unknown"

        # 找第一笔转入 dev 的交易
        for tx in txs:

            to_addr = tx.get("to")

            if to_addr and to_addr.lower() == dev.lower():
                return tx["from"]

        return txs[0]["from"]

    except Exception as e:

        print("查funder失败:", e)

        return "unknown"

    def process(self, dev, token):

        if token in self.seen:
            return

        self.seen.add(token)

        print("处理token:", token)

        try:

            name = get_token_name(self.w3, token)

        except:
            name = "unknown"

        try:

            bnb = get_bnb_balance(self.w3, dev)

        except:
            bnb = 0

        funder = self.get_first_funder(dev)

        msg = f"""
🚀 发现新币

Token
{name}

Token地址
{token}

Dev
{dev}

Dev BNB
{bnb:.3f}

第一笔资金
{funder}

https://bscscan.com/token/{token}
"""

        print("发送TG")

        send(msg)

    def run(self):

        event_filter = self.contract.events.TokenCreated.create_filter(
            fromBlock="latest"
        )

        print("监听创币器...")

        send("🔍 创币器监听已启动")

        while True:

            try:

                events = event_filter.get_new_entries()

                for e in events:

                    dev = e["args"]["owner"]
                    token = e["args"]["token"]

                    print("新token:", token)

                    self.process(dev, token)

            except Exception as e:

                print("监听错误:", e)

                send(f"⚠️ 监听错误\n{e}")

                time.sleep(5)

            time.sleep(3)
