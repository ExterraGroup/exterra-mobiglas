import rocksdb


class RocksdbInstance(type):
    _instances = {}

    def __call__(cls, db_name=None, *args, **kwargs):
        if cls not in cls._instances:
            opts = rocksdb.Options()
            opts.create_if_missing = True
            opts.max_open_files = 300000
            opts.write_buffer_size = 67108864
            opts.max_write_buffer_number = 3
            opts.target_file_size_base = 67108864

            opts.table_factory = rocksdb.BlockBasedTableFactory(
                filter_policy=rocksdb.BloomFilterPolicy(10),
                block_cache=rocksdb.LRUCache(2 * (1024 ** 3)),
                block_cache_compressed=rocksdb.LRUCache(500 * (1024 ** 2)))

            cls.db = rocksdb.DB(db_name, opts)  # todo: db configuration
            cls._instances[cls] = super(RocksdbInstance, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class DataStore(metaclass=RocksdbInstance):

    def get(self, key, type=None):

        raw_value = self.db.get(self.prepare_key(key))
        if raw_value is None:  # key not found
            return "null"
        value = raw_value.decode()

        if value == "None":  # key found but value is None
            return None

        if type == bool:
            return eval(value)
        elif type == int:
            return int(value)
        elif type == float:
            return float(value)
        else:
            return value

    def put(self, key, value=None):
        self.db.put(*self.prepare(key, value))

    def prepare_key(self, key):
        if type(key) is bytes:
            return key
        elif type(key) is str:
            return key.encode()
        elif type(key) is int:
            return str(key).encode()
        else:
            raise ValueError("Unsupported key type.")

    def prepare_value(self, value):
        if type(value) is bytes:
            return value
        elif value is None:
            return b"None"
        elif type(value) is str:
            return value.encode()
        elif type(value) is int or type(value) is bool:
            return str(value).encode()
        elif type(value) is float:
            return str(value).encode()
        else:
            raise ValueError("Unsupported value type.")

    def prepare(self, key, value):
        return self.prepare_key(key), self.prepare_value(value)

    def batch(self, batch: rocksdb.WriteBatch):
        self.db.write(batch)

    def exists(self, key):
        if key is None:
            return False

        if self.get(self.prepare_key(key)) is "null":
            return False
        else:
            return True

    def scan(self):
        it = self.db.iterkeys()
        it.seek_to_first()
        return list(it)

    def full_scan(self):
        it = self.db.iteritems()
        it.seek_to_first()
        return list(it)