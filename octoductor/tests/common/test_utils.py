import unittest

from common.utils import ts

class TestUtils(unittest.TestCase):
    def test_ts(self):
        from datetime import datetime
        import dateutil
        assert dateutil.parser.isoparse(ts()).day == datetime.utcnow().day
