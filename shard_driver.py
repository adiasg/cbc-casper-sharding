from eth_keys import keys
from eth_utils import decode_hex
from eth_typing import Address
from eth import constants
from eth.chains.base import MiningChain
from eth.vm.forks.byzantium import ByzantiumVM
from eth.db.atomic import AtomicDB
from eth.consensus.pow import mine_pow_nonce
from web3.auto import w3
from config import GENESIS_PARAMS, GENESIS_STATE, SHARD_PARAMS, MAGIC_PRI_KEY, MAGIC_ADDRESS
from shard import Shard
from eth.vm.forks.byzantium.transactions import ByzantiumTransaction
from message import Message

class ShardDriver:
    def __init__(self, genesis_params=GENESIS_PARAMS, genesis_state=GENESIS_STATE, shard_params=SHARD_PARAMS):
        self.shard = Shard(genesis_params=genesis_params, genesis_state=genesis_state, shard_params=shard_params)
        self.shard.make_chain()

    def submit_msg(self, msg):
        assert isinstance(msg, bytes), "Expected pickled msg (bytes)"
        msg_obj = Message.deserialize(msg)
        self.shard.submit_msg(msg_obj)

    def submit_tx(self, tx):
        tx = ByzantiumTransaction.deserialize(tx)
        self.shard.submit_tx(tx)

    def mine_next_block(self):
        return self.shard.mine_next_block()

    def get_account_balance(self, address):
        assert isinstance(address, bytes), "Expected address of type bytes"
        return self.shard.vm.state.account_db.get_balance(address)
