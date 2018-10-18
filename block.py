from shard import Shard

class Block:
    def __init__(self, block_hash, shard):
        assert isinstance(shard, Shard), "Expected shard of type Shard"
        assert isinstance(block_hash, bytes), "Expected block_hash of type bytes"
        self.shard = shard
        self.block = shard.chain.get_block_by_hash(block_hash)
        self.sent_log = shard.sent_log[block_hash]
        self.recv_log = shard.recv_log[block_hash]
        self.source = shard.source[block_hash]
