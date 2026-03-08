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

CREATOR = Web3.to_checksum_address(
    "0x8480d0795615b535fb17392c24b42ea283b6f863"
)

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

            r = requests.get(
                ETHERSCAN,
                params=params,
                timeout=10
            ).json()

            if r["status"] != "1":
                return None

            txs = r["result"]

            for tx in txs:

                if tx["to"] and tx["to"].lower() == addr.lower():

                    funder = tx["from"].lower()

                    self.funder_cache[addr] = funder

                    return funder

        except:
            pass

        return None

    def trace_funding(self, dev):

        path = []

        current = dev.lower()

        for _ in range(3):

            funder = self.get_first_funder(current)

            if not funder:
                break

            if funder in CEX:
                path.append(CEX[funder])
                break

            path.append(funder[:6])

            current = funder

        return " -> ".join(path)
def trace_cex_path(self, dev):

    path = []
    current = dev.lower()

    for depth in range(4):

        funder = self.get_first_funder(current)

        if not funder:
            break

        funder = funder.lower()

        # 如果是交易所
        if funder in CEX:

            path.append(CEX[funder])

            return path

        path.append(funder)

        current = funder

    return path
    def format_path(self, path):

    out = []

    for p in path:

        if p in CEX.values():
            out.append(p)

        else:
            out.append(p[:6])

    return " -> ".join(out)
    path = self.trace_cex_path(dev)

path_text = self.format_path(path)
    def scan(self):

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

                    token = log["address"]

                    if token in self.seen:
                        continue

                    self.seen.add(token)

                    dev = Web3.to_checksum_address(
                        log["topics"][1][-20:].hex()
                    )

                    name = get_token_name(token)

                    funder = self.get_first_funder(dev)

                    path = self.trace_funding(dev)

                    bnb = get_bnb_balance(dev)

                    msg = f"""
🚀 New Token

Name: {name}

Token:
{token}

Dev:
{dev}

BNB:
{bnb:.3f}

Funding Path:
{path}
"""

                    send(msg)

                    print(msg)

                self.last_block = latest

            except Exception as e:

                print("scan error:", e)

            time.sleep(2)


if __name__ == "__main__":

    scanner = Scanner()

    print("scanner started")

    scanner.scan()
