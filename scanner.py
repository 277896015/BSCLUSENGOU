import time
from web3 import Web3
from utils import get_token_name, get_bnb_balance
from tg import send

CREATOR = Web3.to_checksum_address(
    "0x8480d0795615b535fb17392c24b42ea283b6f863"
)

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

    # 改成 logs 查询（非常快）
    def get_first_funder(self, dev):

        try:

            latest = self.w3.eth.block_number
            start = latest - 50000

            logs = self.w3.eth.get_logs({
                "fromBlock": start,
                "toBlock": latest,
                "topics": [
                    TRANSFER_TOPIC,
                    None,
                    Web3.to_hex(
                        Web3.to_bytes(
                            hexstr=dev
                        ).rjust(32, b'\0')
                    )
                ]
            })

            if logs:

                tx = self.w3.eth.get_transaction(
                    logs[0]["transactionHash"]
                )

                return tx["from"]

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
