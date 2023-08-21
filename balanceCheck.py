from web3 import Web3
import os
from dotenv import load_dotenv


load_dotenv()


infura_url = os.getenv('PROVIDER')
web3 = Web3(Web3.HTTPProvider(infura_url))

contract_address = os.getenv('CONTRACT_ADDRESS')  

while True:
    balance_wei = web3.eth.get_balance(contract_address)
    balance_eth = web3.from_wei(balance_wei, 'ether')  # Convert wei to ether


    if float(balance_eth) >= 0.025:
        print(f"Contract balance: {balance_eth} ETH")
        print(f"Contract balance: {balance_wei} WEI")
