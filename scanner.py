import time
import os
from web3 import Web3
from utils import get_token_name, get_bnb_balance
from tg import send

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

                    msg = f"""
🚀 **新币上线**

**名称**: {name}
**Token**: `{token}`
**Dev**: `{dev}`
**Dev BNB**: {bnb:.4f} BNB
"""

                    send(msg)

                self.last_block = latest

            except Exception as e:
                print("scan error:", e)

            time.sleep(3)


if __name__ == "__main__":
    s = Scanner()
    s.scan()
