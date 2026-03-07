import os
from web3 import Web3
from scanner import Scanner

RPC_URL = os.getenv("RPC_URL")

w3 = Web3(Web3.HTTPProvider(RPC_URL))

if not w3.is_connected():
    print("RPC连接失败")
    exit()

print("RPC连接成功")

scanner = Scanner(w3)
scanner.run()