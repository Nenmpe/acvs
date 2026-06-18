from web3 import Web3
from web3.exceptions import TransactionNotFound
from django.conf import settings

BLOCKCHAIN_CONFIRMED = 'confirmed'
BLOCKCHAIN_INVALID = 'invalid'
BLOCKCHAIN_PENDING = 'pending'
BLOCKCHAIN_UNAVAILABLE = 'unavailable'
BLOCKCHAIN_NO_TX = 'no_tx'

CONNECTIVITY_TIMEOUT_SECONDS = 10

w3 = Web3(Web3.HTTPProvider(
    settings.BLOCKCHAIN_RPC_URL,
    request_kwargs={'timeout': CONNECTIVITY_TIMEOUT_SECONDS},
))

ACCOUNT = settings.BLOCKCHAIN_ACCOUNT
PRIVATE_KEY = settings.BLOCKCHAIN_PRIVATE_KEY


def is_blockchain_configured():
    return bool(
        settings.BLOCKCHAIN_RPC_URL
        and settings.BLOCKCHAIN_ACCOUNT
        and settings.BLOCKCHAIN_PRIVATE_KEY
    )


def check_blockchain_connectivity():
    if not is_blockchain_configured():
        return False

    try:
        if not w3.is_connected():
            return False
        w3.eth.block_number
        return True
    except Exception:
        return False


def store_hash_on_blockchain(credential_hash_value):
    nonce = w3.eth.get_transaction_count(ACCOUNT)

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
    if not tx_hash:
        return BLOCKCHAIN_NO_TX

    try:
        tx = w3.eth.get_transaction(tx_hash)
    except TransactionNotFound:
        return BLOCKCHAIN_PENDING
    except Exception:
        return BLOCKCHAIN_UNAVAILABLE

    try:
        receipt = w3.eth.get_transaction_receipt(tx_hash)
    except TransactionNotFound:
        return BLOCKCHAIN_PENDING
    except Exception:
        return BLOCKCHAIN_UNAVAILABLE

    if receipt.status != 1:
        return BLOCKCHAIN_INVALID

    if tx['from'].lower() != ACCOUNT.lower():
        return BLOCKCHAIN_INVALID

    stored_data = tx.input
    decoded = Web3.to_text(stored_data).strip().lower()
    original_hash = original_hash.strip().lower()

    if decoded == original_hash:
        return BLOCKCHAIN_CONFIRMED

    return BLOCKCHAIN_INVALID
