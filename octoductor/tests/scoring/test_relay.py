import unittest
from scoring.relay import index

class TestRelay(unittest.TestCase):
    def test_relay(self):
        event = '{"hello": "world"}'
        self.assertEquals(index.handler(event, None), event)
