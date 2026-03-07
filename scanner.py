import time
from web3 import Web3
from utils import get_token_name, get_bnb_balance
from tg import send

CREATOR = Web3.to_checksum_address("0x8480d0795615b535fb17392c24b42ea283b6f863")

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

class Scanner:

    def __init__(self, w3):

        self.w3 = w3

        self.contract = w3.eth.contract(
            address=CREATOR,
            abi=CREATOR_ABI
        )

        self.seen = set()

    def get_first_funder(self, address):

        latest = self.w3.eth.block_number
        start = latest - 200000

        if start < 1:
            start = 1

        for block in range(start, latest):

            try:

                b = self.w3.eth.get_block(
                    block,
                    full_transactions=True
                )

                for tx in b.transactions:

                    if tx["to"] and tx["to"].lower() == address.lower():
                        return tx["from"]

            except:
                pass

        return "unknown"

    def process(self, dev, token):

        if token in self.seen:
            return

        self.seen.add(token)

        name = get_token_name(self.w3, token)
        bnb = get_bnb_balance(self.w3, dev)
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

        send(msg)

    def run(self):

        event_filter = self.contract.events.TokenCreated.create_filter(
            from_block="latest"
        )

        print("监听创币器...")

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
                time.sleep(5)

            time.sleep(3)
