import unittest

from mobiglas.time import add_hours


class TimeTest(unittest.TestCase):

    def test_add_hours(self):
        #  Sunday, June 30, 2019 12:00:00 PM
        # 1561896000000
        epoch = 1561896000000
        actual = add_hours(epoch, 1)
        self.assertEqual(actual, 1561899600000)
