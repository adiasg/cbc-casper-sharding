import pickle
from eth_utils import decode_hex, encode_hex
from eth.vm.forks.byzantium.transactions import ByzantiumTransaction

class Message:
    def __init__(self, base_hash, TTL, target_shard_id, tx, shard):
        self.base_hash = base_hash
        self.TTL = TTL
        self.target_shard_id = target_shard_id
        self.tx = tx
        assert self.check_validity(shard)

    def verify_base_in_target(self, shard):
        assert isinstance(self.target_shard_id, int), "Expected integer target_shard_id"
        # TODO: This check was a cheap hack in lack of py-evm documentation
        return self.base_hash == shard.chain.get_block_by_hash(self.base_hash).header.hash, "Couldn't find block with specified base_hash in target shard"

    def serialize(self):
        return pickle.dumps(self)

    @staticmethod
    def deserialize(obj):
        return pickle.loads(obj)

    def check_validity(self, shard):
        assert isinstance(self.target_shard_id, int), "Expected integer target_shard_id"
        assert isinstance(self.base_hash, bytes), "Expected target_shard_id of type bytes"
        assert type(shard).__name__ == 'Shard', "Expected shard of type Shard"
        assert self.verify_base_in_target(shard), "Expected base in target shard"
        assert isinstance(self.TTL, int), "Expected integer TTL"
        assert isinstance(self.tx, ByzantiumTransaction), "Expected tx of type ByzantiumTransaction"
        self.tx.check_signature_validity()
        assert self.tx.is_signature_valid, "Expected valid signature on tx"
        return True

    def __str__(self, prefix='\t'):
        x =  prefix+"base_hash:\t"+encode_hex(self.base_hash)+'\n'
        x += prefix+"TTL:\t\t"+str(self.TTL)+'\n'
        x += prefix+"target_shard_id:"+str(self.target_shard_id)+'\n'
        x += prefix+"tx:\n"
        x += prefix+"\tsender:\t"+encode_hex(self.tx.sender)+'\n'
        x += prefix+"\tto:\t"+encode_hex(self.tx.to)+'\n'
        x += prefix+"\tvalue:\t"+str(self.tx.value)+'\n'
        return x
