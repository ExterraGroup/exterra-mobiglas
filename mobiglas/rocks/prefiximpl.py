import rocksdb


class PrefixImpl(rocksdb.interfaces.SliceTransform):

    def __init__(self, prefix):
        self.prefix = prefix
        self.prefix_len = len(prefix)

    def name(self):
        return b"nameprefix"

    def transform(self, src):
        return 0, self.prefix_len

    def in_domain(self, src):
        return len(src) >= self.prefix_len

    def in_range(self, prefix):
        return prefix == self.prefix
