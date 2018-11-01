from eth_keys import keys
from eth_utils import decode_hex, encode_hex
from eth_typing import Address
from eth import constants
from eth.chains.base import MiningChain
from eth.vm.forks.byzantium import ByzantiumVM
from eth.db.atomic import AtomicDB
from eth.consensus.pow import mine_pow_nonce
# from web3.auto import w3
from block import Block
from message import Message
from config import GENESIS_PARAMS, SHARD_PARAMS, MAGIC_PRI_KEY, MAGIC_ADDRESS, MSG_LOGGER_CONTRACT, w3

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
        self.blocks = []
        self.msg_mempool = []

    def make_chain(self):
        klass = MiningChain.configure( __name__='Shard{}Chain'.format(self.shard_id), vm_configuration=( (constants.GENESIS_BLOCK_NUMBER, ByzantiumVM), ) )
        self.chain = klass.from_genesis(AtomicDB(), self.genesis_params, self.genesis_state)
        self.vm = self.chain.get_vm()
        print("Shard " + str(self.shard_id) + " was initialized")
        print("Parent Shard ID:", self.parent_id)
        print("Child Shard IDs:", self.child_ids)
        print("\tAccounts on this shard are:")
        for address in self.accounts['addresses']:
            print("\t\t", encode_hex(address))
        print("\tMagic Account is:")
        print("\t\t", encode_hex(MAGIC_ADDRESS))
        return self.chain

    def get_block(self, block_header):
        return self.chain.get_block_by_header(block_header)

    def submit_tx(self, signed_tx):
        if (signed_tx.sender in self.accounts['addresses'] or signed_tx.sender == MAGIC_ADDRESS) and (signed_tx.to in self.accounts['addresses'] or signed_tx.to == MAGIC_ADDRESS):
        # TODO verify that accounts are in this shard
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

    def submit_msg(self, msg):
        assert isinstance(msg, Message), "Expected msg of type Message"
        assert msg.check_validity(self), "Invalid message!"
        self.msg_mempool.append(msg)

    def choose_messages_from_mempool(self, num_of_messages=None):
        if num_of_messages is None:
            num_of_messages = len(self.msg_mempool)
        chosen_msgs = []
        for i in range(num_of_messages):
            chosen_msgs.append(self.msg_mempool[i])
        return chosen_msgs

    def generate_tx_from_msg(self, msg):
        # TODO: Perhaps this check should be in the client, and not the Shard class
        # TODO 'msg.base_hash == self.chain.get_block_by_hash(msg.base_hash).header.hash' is a check hack in lack of py-evm documentation
        assert msg.target_shard_id == self.shard_id, "Expected target_shard_id to be this shard"
        assert msg.tx.to in self.accounts['addresses'], "Expected 'to' in this shard's accounts"
        assert msg.base_hash == self.chain.get_block_by_hash(msg.base_hash).header.hash, "Expected base in this shard"
        magic_sender_pri_key = keys.PrivateKey(decode_hex(MAGIC_PRI_KEY))
        magic_sender_address = Address(magic_sender_pri_key.public_key.to_canonical_address())
        nonce = self.vm.state.account_db.get_nonce(magic_sender_address)
        tx = self.vm.create_unsigned_transaction(
                    nonce=nonce,
                    gas_price=msg.tx.gas_price,
                    gas=msg.tx.gas,
                    to=msg.tx.to,
                    value=msg.tx.value,
                    # TODO: data should reflect message info
                    data='msg_data'.encode('utf-8'),
                )
        tx = tx.as_signed_transaction(magic_sender_pri_key)
        return tx

    def generate_msg_tx_tuples(self, chosen_msgs):
        msg_tx_tuples = [ (msg, self.generate_tx_from_msg(msg)) for msg in chosen_msgs ]
        return msg_tx_tuples

    def process_msg_mempool(self, num_of_messages=None):
        # WARNING: This will remove messages from msg_mempool and put corresponding tx in chain.apply_transaction. Better call mine_next_block() immediately after this.
        msg_tx_tuple = self.generate_msg_tx_tuples(self.choose_messages_from_mempool(num_of_messages))
        for x in msg_tx_tuple:
            self.submit_tx(x[1])
            self.msg_mempool.remove(x[0])

    def make_tx_emit_msg_as_event(self, msg):
        assert isinstance(msg, Message), "Expected msg to be a Message"
        # function send(uint _shard_ID, uint _sendGas, address _sendToAddress, bytes _data)
        call = MSG_LOGGER_CONTRACT.functions.send()

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
