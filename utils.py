from web3 import Web3

KUCOIN = "0x689c56aef474df92d44a1b70850f808488f9769c"

def get_token_name(w3, token):
    abi = [
        {
            "name": "name",
            "outputs": [{"type": "string"}],
            "inputs": [],
            "stateMutability": "view",
            "type": "function"
        }
    ]
    try:
        c = w3.eth.contract(address=token, abi=abi)
        return c.functions.name().call()
    except:
        return "Unknown"

def get_bnb_balance(w3, addr):
    try:
        balance = w3.eth.get_balance(addr)
        return w3.from_wei(balance, "ether")
    except:
        return 0.0
