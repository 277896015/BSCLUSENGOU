import os
from web3 import Web3
from scanner import Scanner

RPC = os.getenv("RPC")

if not RPC:
    print("❌ 未设置环境变量 RPC")
    exit(1)

w3 = Web3(Web3.HTTPProvider(RPC))
print("✅ RPC连接成功" if w3.is_connected() else "❌ RPC连接失败")
send("创币器监控启动成功")
if __name__ == "__main__":
    scanner = Scanner()
    scanner.scan()
