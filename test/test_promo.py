import unittest

import data
from promo import address_set


class TestAddressReading(unittest.TestCase):
    def test_address_reading(self):
        expected = ["abc@jd.de", "123@ww.xy", "ods@sdf.com",
                    "bbb@ww.de", "gs@kdj.de", "sdfo@foo",
                    "idsjf@osefj"]

        addrs = [addr for addr in address_set(data.get_path("addresses"))]

        self.assertEqual(sorted(addrs), sorted(expected))