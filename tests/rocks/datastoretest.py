import unittest

from mobiglas.rocks.datastore import DataStore

ds = DataStore("~/unittest.db")


class DataStoreTest(unittest.TestCase):

    # test prepare_key
    def test_prepare_key_bytes(self):
        key = b"some-bytes"
        actual = ds.prepare_key(key)
        self.assertEqual(actual, key)

    def test_prepare_key_string(self):
        key = "some-key"
        actual = ds.prepare_key(key)
        self.assertEqual(actual, key.encode())

    def test_prepare_key_int(self):
        key = 123
        actual = ds.prepare_key(key)
        self.assertEqual(actual, str(123).encode())

    def test_prepare_key_NoneType(self):
        with self.assertRaises(ValueError):
            ds.prepare_key(None)

    # test prepare_value
    def test_prepare_value_bytes(self):
        value = b"some-bytes"
        actual = ds.prepare_value(value)
        self.assertEqual(actual, value)

    def test_prepare_value_None(self):
        actual = ds.prepare_value(None)
        self.assertEqual(actual, b"None")

    def test_prepare_value_str(self):
        value = "some-string"
        actual = ds.prepare_value(value)
        self.assertEqual(actual, value.encode())

    def test_prepare_value_True(self):
        value = True
        actual = ds.prepare_value(value)
        self.assertEqual(actual, str(value).encode())

    def test_prepare_value_False(self):
        value = False
        actual = ds.prepare_value(value)
        self.assertEqual(actual, str(value).encode())

    def test_prepare_value_int(self):
        value = 123
        actual = ds.prepare_value(value)
        self.assertEqual(actual, str(value).encode())

    def test_prepare_value_float(self):
        value = 123.0
        actual = ds.prepare_value(value)
        self.assertEqual(actual, str(value).encode())

    def test_prepare_kv(self):
        key = 1
        value = 2
        actual = ds.prepare(key, value)
        self.assertEqual(actual, (str(key).encode(), str(value).encode()))

    # test get
    def test_get_bytesValue(self):
        key = b"test_get_bytes"
        value = b"value"
        ds.put(key, value)
        actual = ds.get(key)
        self.assertEqual(actual, value.decode())

    def test_get_NoneValue(self):
        key = b"test_get_NoneValue"
        value = None
        ds.put(key, value)
        actual = ds.get(key)
        self.assertEqual(actual, value)

    def test_get_boolTrueValue(self):
        key = b"test_get_boolTrueValue"
        value = True
        ds.put(key, value)
        actual = ds.get(key, bool)
        self.assertEqual(actual, value)

    def test_get_boolFalseValue(self):
        key = b"test_get_boolFalseValue"
        value = False
        ds.put(key, value)
        actual = ds.get(key, bool)
        self.assertEqual(actual, value)

    def test_get_intValue(self):
        key = b"test_get_intValue"
        value = 123
        ds.put(key, value)
        actual = ds.get(key, int)
        self.assertEqual(actual, value)

    def test_get_floatValue(self):
        key = b"test_get_floatValue"
        value = 123.0
        ds.put(key, value)
        actual = ds.get(key, float)
        self.assertEqual(actual, value)

    # test exists
    def test_exists_keyNone(self):
        self.assertFalse(ds.exists(None))

    def test_exists_keyNotFound(self):
        self.assertFalse(ds.exists(123))

    def test_exists_valueNone(self):
        key = b"test_exists_valueNone"
        ds.put(key)
        self.assertTrue(ds.exists(key))

    def test_exists_valueStr(self):
        key = b"test_exists_valueNone"
        value = "string"
        ds.put(key, value)
        self.assertTrue(ds.exists(key))
