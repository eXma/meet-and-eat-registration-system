import os

import locale
import unittest
import mock
from datetime import datetime
import cfg
from cfg import parse_cfg_date, _fix_locale, pretty_date, config


class TestDateHandling(unittest.TestCase):
    def test_date_parsing(self):
        test_date = "2015-01-02 18:06"
        parsed = parse_cfg_date(test_date)
        self.assertEquals(parsed, datetime(2015, 01, 02, 18, 06))

    def test_locale_set(self):
        oldloc = locale.getlocale(locale.LC_TIME)
        locale.setlocale(locale.LC_TIME, "C")
        self.assertEquals(locale.getlocale(locale.LC_TIME)[0], None)
        with _fix_locale("de_DE"):
            self.assertEquals(locale.getlocale(locale.LC_TIME)[0], "de_DE")
        self.assertEquals(locale.getlocale(locale.LC_TIME)[0], None)

    def test_date_format(self):
        date = datetime(2015, 10, 17, 18, 06)

        self.assertEquals(pretty_date(date), "17.10.")
        self.assertEquals(pretty_date(date, show_year=True), "17.10.2015")
        self.assertEquals(pretty_date(date, month_name=True), "17. Oktober")
        self.assertEquals(pretty_date(date, with_weekday=True), "Samstag, den 17.10.")
        self.assertEquals(pretty_date(date, show_year=True, month_name=True),
                          "17. Oktober 2015")
        self.assertEquals(pretty_date(date, show_year=True, month_name=True, with_weekday=True),
                          "Samstag, den 17. Oktober 2015")


class TestConfigLoading(unittest.TestCase):
    def setUp(self):
        self.fname = os.path.join(os.path.dirname(__file__), "data", "config_example.yaml")
        cfg.config.clear()

    def test_load_file_arg(self):
        self.assertRaises(AssertionError, lambda: config.DB_CONNECTION)
        self.assertRaises(AssertionError, cfg.load_config)
        cfg.load_config(self.fname)

        self.assertIsNotNone(config.DB_CONNECTION)

    def test_load_file_env(self):
        self.assertRaises(AssertionError, lambda: config.DB_CONNECTION)

        with mock.patch("os.getenv", return_value=self.fname):
            cfg.load_config()

        self.assertIsNotNone(config.DB_CONNECTION)