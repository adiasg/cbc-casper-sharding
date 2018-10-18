from eth import constants
from web3.auto import w3
from eth_keys import keys
from eth_typing import Address
from eth_utils import decode_hex, to_wei
# from eth.chains.base import MiningChain
# from eth.vm.forks.byzantium import ByzantiumVM
# from eth.db.atomic import AtomicDB
# from eth.consensus.pow import mine_pow_nonce

GENESIS_PARAMS = {
    'parent_hash': constants.GENESIS_PARENT_HASH,
    'uncles_hash': constants.EMPTY_UNCLE_HASH,
    'coinbase': constants.ZERO_ADDRESS,
    'transaction_root': constants.BLANK_ROOT_HASH,
    'receipt_root': constants.BLANK_ROOT_HASH,
    'difficulty': 1,
    'block_number': constants.GENESIS_BLOCK_NUMBER,
    'gas_limit': constants.GENESIS_GAS_LIMIT,
    'timestamp': 1539724066,
    'extra_data': constants.GENESIS_EXTRA_DATA,
    'nonce': constants.GENESIS_NONCE
}

def convert_pri_key_to_address(pri_key):
    return Address(keys.PrivateKey(decode_hex(pri_key)).public_key.to_canonical_address())

MAGIC_PRI_KEY = w3.eth.account.create().privateKey.hex()
MAGIC_ADDRESS = convert_pri_key_to_address(MAGIC_PRI_KEY)
MAGIC_FUNDS = to_wei(100000, 'ether')

GENESIS_STATE = {
    MAGIC_ADDRESS: {
        'balance': MAGIC_FUNDS,
        'nonce': 0,
        'code': b'',
        'storage': {}
    }
}

private_keys = [w3.eth.account.create().privateKey.hex() for x in range(10)]
addresses = [convert_pri_key_to_address(pri_key) for pri_key in private_keys]


SHARD_PARAMS = {
    'shard_id': 3,
    'parent_id': 1,
    'child_ids': [4, 5],
    'accounts': {
                    'private_keys': private_keys,
                    'addresses': addresses
                }
}

OUT_OF_SHARD_PRI_KEYS = [w3.eth.account.create().privateKey.hex() for x in range(10)]
OUT_OF_SHARD_ADDRESSES = [convert_pri_key_to_address(pri_key) for pri_key in OUT_OF_SHARD_PRI_KEYS]
