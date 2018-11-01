from eth import constants
from web3.auto import w3
from eth_keys import keys
from eth_typing import Address
from eth_utils import decode_hex, encode_hex, to_wei
from web3 import Web3
# from eth.chains.base import MiningChain
# from eth.vm.forks.byzantium import ByzantiumVM
# from eth.db.atomic import AtomicDB
# from eth.consensus.pow import mine_pow_nonce

SHARD_IDS = [1, 3, 4, 5]

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

MSG_LOGGER_BIN = "0x6080604052601e60005534801561001557600080fd5b5061020b806100256000396000f300608060405260043610610041576000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff168063e09ee87014610046575b600080fd5b6100d46004803603810190808035906020019092919080359060200190929190803573ffffffffffffffffffffffffffffffffffffffff169060200190929190803590602001908201803590602001908080601f01602080910402602001604051908101604052809392919081815260200183838082843782019150505050505091929192905050506100d6565b005b438273ffffffffffffffffffffffffffffffffffffffff16857fe9fbdfd23831dbc2bdec9e9ef0d5ac734f56996d4211992cc083e97f2770ba4286333487600054604051808681526020018573ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200184815260200180602001838152602001828103825284818151815260200191508051906020019080838360005b8381101561019b578082015181840152602081019050610180565b50505050905090810190601f1680156101c85780820380516001836020036101000a031916815260200191505b50965050505050505060405180910390a4505050505600a165627a7a72305820935f0c70b80b835cecc16806f978ca84fc37ce193c963bc8d519af52e9ba89f70029"
MSG_LOGGER_ABI = '[{"constant":false,"inputs":[{"name":"_shard_ID","type":"uint256"},{"name":"_sendGas","type":"uint256"},{"name":"_sendToAddress","type":"address"},{"name":"_data","type":"bytes"}],"name":"send","outputs":[],"payable":true,"stateMutability":"payable","type":"function"},{"anonymous":false,"inputs":[{"indexed":true,"name":"shard_ID","type":"uint256"},{"indexed":false,"name":"sendGas","type":"uint256"},{"indexed":false,"name":"sendFromAddress","type":"address"},{"indexed":true,"name":"sendToAddress","type":"address"},{"indexed":false,"name":"value","type":"uint256"},{"indexed":false,"name":"data","type":"bytes"},{"indexed":true,"name":"base","type":"uint256"},{"indexed":false,"name":"TTL","type":"uint256"}],"name":"SentMessage","type":"event"}]'

GENESIS_STATE = {
    MAGIC_ADDRESS: {
        'balance': MAGIC_FUNDS,
        'nonce': 0,
        'code': decode_hex(MSG_LOGGER_BIN),
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

w3 = Web3()
w3.eth.defaultAccount = encode_hex(MAGIC_ADDRESS)

MSG_LOGGER_CONTRACT = w3.eth.contract(
    address=MAGIC_ADDRESS,
    abi=MSG_LOGGER_ABI,
)
