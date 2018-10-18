from eth_keys import keys
from eth_utils import decode_hex, encode_hex
from eth_typing import Address
from eth import constants
from eth.chains.base import MiningChain
from eth.vm.forks.byzantium import ByzantiumVM
from eth.db.atomic import AtomicDB
from eth.consensus.pow import mine_pow_nonce
# from web3.auto import w3
from message import Message
from config import GENESIS_PARAMS, SHARD_PARAMS, MAGIC_PRI_KEY, MAGIC_ADDRESS

class Shard:
    def __init__(self, genesis_params, genesis_state, shard_params):
        self.genesis_params = genesis_params
        self.genesis_state = genesis_state
        self.shard_params = shard_params
        self.shard_id = shard_params['shard_id']
        self.parent_id = shard_params['parent_id']
        self.child_ids = shard_params['child_ids']
        self.accounts = shard_params['accounts']
        self.chain = None
        self.vm = None
        # Sent Log: {block_hash: [sent msg list]}
        self.sent_log = {}
        # Received Log: {block_hash: [received msg list]}
        self.recv_log = {}
        # Sources: {block_hash: [sent msg list]}
        self.source = {}
        self.msg_mempool = []

    def make_chain(self):
        klass = MiningChain.configure( __name__='Shard{}Chain'.format(self.shard_id), vm_configuration=( (constants.GENESIS_BLOCK_NUMBER, ByzantiumVM), ) )
        self.chain = klass.from_genesis(AtomicDB(), self.genesis_params, self.genesis_state)
        self.vm = self.chain.get_vm()
        print("Shard " + str(self.shard_id) + " was initialized")
        print("\tAccounts on this shard are:")
        for address in self.accounts['addresses']:
            print("\t\t", encode_hex(address))
        print("\tMagic Account is:")
        print("\t\t", encode_hex(MAGIC_ADDRESS))
        return self.chain

    def submit_tx(self, signed_tx):
        # TODO verify that accounts are in this shard
        if (signed_tx.sender in self.accounts['addresses'] or signed_tx.sender == MAGIC_ADDRESS) and signed_tx.to in self.accounts['addresses']:
            self.chain.apply_transaction(signed_tx)
        elif signed_tx.sender in self.accounts['addresses'] and signed_tx.to not in self.accounts['addresses']:
            assert False, "*** OUTGOING MESSAGE SUBMITTED ***"
        else:
            assert False, "All cases above have failed"

    def update_shard(self, new_block, new_messages):
        self.vm = self.chain.vm
        if new_block.header.parent_hash == GENESIS_PARAMS['parent_hash']:
            self.sent_log[new_block.hash] = []
        else:
            self.sent_log[new_block.hash] = self.sent_log[new_block.header.parent_hash] + new_messages

    def mine_next_block(self):
        block = self.chain.get_vm().finalize_block(self.chain.get_block())
        nonce, mix_hash = mine_pow_nonce(
                                block.number,
                                block.header.mining_hash,
                                block.header.difficulty
                            )
        self.chain.mine_block(mix_hash=mix_hash, nonce=nonce)
        self.vm = self.chain.get_vm()
        return self.chain.get_block_by_header(self.chain.get_canonical_head())

    def get_block(self, block_header):
        return self.chain.get_block_by_header(block_header)

    def submit_msg(self, msg):
        assert isinstance(msg, Message)
        self.msg_mempool.append(msg)

    def empty_msg_mempool(self):
        for msg in self.msg_mempool:
            # print(msg)
            # TODO: Perhaps this check should be in the client, and not the Shard class
            # print("target_shard_id:", msg.target_shard_id, self.shard_id)
            # print("base_hash", msg.base_hash == self.chain.get_block_by_hash(msg.base_hash).header.hash)
            if msg.target_shard_id == self.shard_id and msg.base_hash == self.chain.get_block_by_hash(msg.base_hash).header.hash:
                if msg.tx.to in self.accounts['addresses']:
                    sender_pri_key = keys.PrivateKey(decode_hex(MAGIC_PRI_KEY))
                    sender_address = Address(sender_pri_key.public_key.to_canonical_address())
                    nonce = self.vm.state.account_db.get_nonce(sender_address)
                    tx = self.vm.create_unsigned_transaction(
                                nonce=nonce,
                                gas_price=msg.tx.gas_price,
                                gas=msg.tx.gas,
                                to=msg.tx.to,
                                value=msg.tx.value,
                                # TODO: data should reflect message info
                                data='msg_data'.encode('utf-8'),
                            )
                    tx = tx.as_signed_transaction(sender_pri_key)
                    self.submit_tx(tx)
            self.msg_mempool.remove(msg)
