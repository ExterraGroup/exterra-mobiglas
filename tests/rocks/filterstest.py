import unittest

from mobiglas.rocks.filters import SuffixFilter, PrefixFilter, ContainsFilter

suffixFilter = ".suffix"
prefixFilter = ("prefix", "pre.1", "pre.2")
containsFilter = "bob"


class SuffixFilterTest(unittest.TestCase):

    def test_match_None(self):
        self.assertFalse(SuffixFilter.match(suffixFilter, None))

    def test_match_True(self):
        self.assertTrue(SuffixFilter.match(suffixFilter, b"prefix.suffix"))

    def test_match_False(self):
        self.assertFalse(SuffixFilter.match(suffixFilter, b"prefix.not"))

    def test_find_None(self):
        self.assertEqual(SuffixFilter.find(suffixFilter, None), [])

    def test_find_1(self):
        self.assertEqual(
            SuffixFilter.find(suffixFilter, [b"prefix.1.suffix", b"prefix.1.other", b"prefix.1.suffix.other"]),
            ["prefix.1.suffix"])


class PrefixFilterTest(unittest.TestCase):

    def test_match_None(self):
        self.assertFalse(PrefixFilter.match(prefixFilter, None))

    def test_match_True(self):
        self.assertTrue(PrefixFilter.match(prefixFilter, b"prefix.foo"))
        self.assertTrue(PrefixFilter.match(prefixFilter, b"pre.1.bar"))
        self.assertTrue(PrefixFilter.match(prefixFilter, b"pre.2.sal"))

    def test_match_False(self):
        self.assertFalse(PrefixFilter.match(prefixFilter, b"word.prefix"))


class ContainsFilterTest(unittest.TestCase):

    def test_match_None(self):
        self.assertFalse(ContainsFilter.match(containsFilter, None))

    def test_match_True(self):
        self.assertTrue(ContainsFilter.match(containsFilter, b"pre.bob"))
        self.assertTrue(ContainsFilter.match(containsFilter, b"pre.bob.1"))
        self.assertTrue(ContainsFilter.match(containsFilter, b"bob.2"))

    def test_match_False(self):
        self.assertFalse(ContainsFilter.match(containsFilter, b"sal.mal"))
