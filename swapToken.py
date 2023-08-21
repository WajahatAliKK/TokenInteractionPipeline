from web3 import Web3
from dotenv import load_dotenv
from models import Transactions
from typing import Optional
from db_client import db
from sqlalchemy.exc import SQLAlchemyError
import os

load_dotenv()


infura_url = os.getenv('PROVIDER')
contract_address = os.getenv('CONTRACT_ADDRESS')
contract_abi = os.getenv('CONTRACT_ABI')

web3 = Web3(Web3.HTTPProvider(infura_url))

def swapToken():
    # Instantiate the contract
    contract = web3.eth.contract(address=contract_address, abi=contract_abi)

    # Your wallet private key (Replace with your actual private key)
    private_key = os.getenv('WALLET_PRIVATE_KEY')

    # Set the account that will sign the transaction
    account = web3.eth.account.from_key(private_key)

    # Specify the gas price and gas limit for the transaction
    gas_price = web3.toWei('30', 'gwei')
    gas_limit = 2000000

    # Desired output amount
    # amount_out_min = web3.toWei(100, 'ether')  # Amount in wei
    amount_out_min = 0

    # Call the swapEthForTokens function
    transaction = contract.functions.swapEthForTokens(amount_out_min).buildTransaction({
        'chainId': 1,  # Mainnet chain ID
        'gasPrice': gas_price,
        'gas': gas_limit,
        'nonce': web3.eth.get_transaction_count(account.address),
    })

    # Sign and send the transaction
    signed_transaction = web3.eth.account.sign_transaction(transaction, private_key)
    transaction_hash = web3.eth.send_raw_transaction(signed_transaction.rawTransaction)
    
    print(f"Transaction hash: {transaction_hash.hex()}")
    # Assuming you have the transaction hash stored in transaction_hash
    transaction_receipt = web3.eth.wait_for_transaction_receipt(transaction_hash)

    if transaction_receipt:
        gas_used = transaction_receipt['gasUsed']
        gas_price = transaction_receipt['gasPrice']

    transaction_fee = gas_used * gas_price
    tx_data = {}
    tx_data['tx_hash'] = transaction_hash
    tx_data['tx_fee'] = transaction_fee
    tx_data['tx_type'] = 'SWAP'
    tx_data['tx_state'] = 'Pending'



async def add_transaction(user_id: int, wallet_id: int, tx_data: dict) -> Optional[Transactions]:
    async with db.Session() as session:
        try:
            transaction = Transactions(
                user_id=user_id,
                wallet_id=wallet_id,
                tx_hash=tx_data['tx_hash'],
                fee=tx_data.get('fee'),
                tx_type=tx_data['tx_type'],
                # time_stamp=tx_data['time_stamp'],
                tx_state=tx_data['tx_state']
            )

            session.add(transaction)
            await session.commit()

            return transaction
        except SQLAlchemyError as e:
            print(f"Error adding transaction: {e}")
            await session.rollback()
            return None  

        except SQLAlchemyError as e:
            print("Error:", e)
            await session.rollback()  

        return None