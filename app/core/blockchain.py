import json
import hashlib
from web3 import Web3
from django.conf import settings

# Connect to Ethereum Testnet (Sepolia)
w3 = Web3(Web3.HTTPProvider(settings.BLOCKCHAIN_RPC_URL))

ACCOUNT = settings.BLOCKCHAIN_ACCOUNT
PRIVATE_KEY = settings.BLOCKCHAIN_PRIVATE_KEY

# def generate_credential_hash(credential):
#     data = f"{credential.student.username}{credential.degree_name}{credential.field_of_study}{credential.issue_date}{credential.grade}"
#     return hashlib.sha256(data.encode()).hexdigest()


def store_hash_on_blockchain(credential_hash_value):
    nonce = w3.eth.get_transaction_count(ACCOUNT)

    '''tx = {
        'nonce': nonce,
        'to': ACCOUNT,  # sending to self (cheap + simple)
        'value': 0,
        'gas': 200000,
        'gasPrice': w3.to_wei('10', 'gwei'),
        'data': w3.to_hex(text=credential_hash_value)
    }
    '''
    tx = {
        'nonce': nonce,
        'to': ACCOUNT,
        'value': 0,
        'gas': 100000,
        'gasPrice': w3.eth.gas_price,
        'chainId': 11155111,
        'data': w3.to_hex(text=credential_hash_value)
    }
    
    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

    return w3.to_hex(tx_hash)


def verify_hash_on_blockchain(tx_hash, original_hash):
    try:
        tx = w3.eth.get_transaction(tx_hash)
        receipt = w3.eth.get_transaction_receipt(tx_hash)

        print(f"Receit Status: {receipt.status}")

        if receipt.status != 1:
            return False

        if tx['from'].lower() != ACCOUNT.lower():
            return False

        stored_data = tx.input

        # decoded = bytes.fromhex(stored_data[2:]).decode()
        if isinstance(stored_data, bytes):
            decoded = stored_data.decode()
        else:
            decoded = stored_data

        decoded = stored_data.decode().strip().lower()
        original_hash = original_hash.strip().lower()

        return decoded == original_hash

    except Exception:
        return False