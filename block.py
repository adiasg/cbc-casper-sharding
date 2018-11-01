from config import SHARD_IDS
import pickle

class Block:
    def __init__(self, block, shard_ID, sent_log, recv_log, source):
        assert block.__class__ == 'eth.vm.forks.byzantium.blocks.ByzantiumBlock', "Expected block of type 'eth.vm.forks.byzantium.blocks.ByzantiumBlock'"
        self.block = block
        assert shard_ID in SHARD_IDS, "Expected shard_ID in SHARD_IDS"
        self.shard_ID = shard_ID
        assert isinstance(sent_log, list), "Expected sent_log to be a list"
        self.sent_log = sent_log
        assert isinstance(recv_log, list), "Expected recv_log to be a list"
        self.recv_log = recv_log
        if not isinstance(source, Block):
            print("In Blocks(): source was not a Block")
            print("Block height is:", block.number)
        self.source = source

    def serialize(self):
        return pickle.dumps(self)

    @staticmethod
    def deserialize(obj):
        block = pickle.loads(obj)
        assert isinstance(block, Block), "deserialized object was not block"
        return block
