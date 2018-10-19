from eth_keys import keys
from eth_utils import decode_hex, encode_hex
from eth_typing import Address
from eth import constants
from eth.chains.base import MiningChain
from eth.vm.forks.byzantium import ByzantiumVM
from eth.db.atomic import AtomicDB
from eth.consensus.pow import mine_pow_nonce
from web3.auto import w3
from config import GENESIS_PARAMS, GENESIS_STATE, SHARD_PARAMS, MAGIC_ADDRESS, OUT_OF_SHARD_PRI_KEYS, OUT_OF_SHARD_ADDRESSES
from shard import Shard
from eth.vm.forks.byzantium.transactions import ByzantiumTransaction
from message import Message
from shard_driver import ShardDriver

def make_sample_tx(sender_pri_key_hex, recv_address, data="sample tx data".encode('utf-8'), nonce=None, value=0):
    assert isinstance(data, bytes), "data must be of type bytes"
    sender_pri_key = keys.PrivateKey(decode_hex(sender_pri_key_hex))
    sender_address = Address(sender_pri_key.public_key.to_canonical_address())
    vm = shard_driver.shard.vm
    if nonce is None:
        nonce = vm.state.account_db.get_nonce(sender_address)
    tx = vm.create_unsigned_transaction(
                nonce=nonce,
                gas_price=0,
                gas=100000,
                to=recv_address,
                value=value,
                data=data,
            )
    return tx.as_signed_transaction(sender_pri_key)

shards = {3: ShardDriver(genesis_params=GENESIS_PARAMS, genesis_state=GENESIS_STATE, shard_params=SHARD_PARAMS)}

shard_driver = shards[3]
print(shard_driver.mine_next_block())

canonical_block = shard_driver.shard.get_block(shard_driver.shard.chain.get_canonical_head())

sample_tx = make_sample_tx(SHARD_PARAMS['accounts']['private_keys'][0], SHARD_PARAMS['accounts']['addresses'][1], data='my sample tx'.encode('utf-8'))

# print(sample_tx.sender)

shard_driver.submit_tx(ByzantiumTransaction.serialize(sample_tx))
print(shard_driver.mine_next_block())

print("Magic Account Balance:", shard_driver.get_account_balance(MAGIC_ADDRESS))

print("Generating message that transfers some amount from an out-of-shard address to an in-shard address")
# print("\tsender:\t", encode_hex(OUT_OF_SHARD_ADDRESSES[0]))
# print("\tto:\t", encode_hex(SHARD_PARAMS['accounts']['addresses'][2]))
# print("\tvalue:\t", 10000)

sample_msg_tx = make_sample_tx(OUT_OF_SHARD_PRI_KEYS[0], SHARD_PARAMS['accounts']['addresses'][2], data='my sample tx'.encode('utf-8'), value=10000)
msg = Message(shard_driver.shard.chain.get_canonical_head().hash, 10, 3, sample_msg_tx, shards[3].shard)
print(msg)
shard_driver.submit_msg(msg.serialize())
shard_driver.shard.empty_msg_mempool()
shard_driver.mine_next_block()

print("Magic Account Balance:", shard_driver.get_account_balance(MAGIC_ADDRESS))
print("Recepient Account Balance:", shard_driver.get_account_balance(SHARD_PARAMS['accounts']['addresses'][2]))
