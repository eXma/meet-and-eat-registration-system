from datetime import datetime

__author__ = 'jan'


def parse_end_date(cfg_date):
    return datetime.strptime(cfg_date, "%Y-%m-%d %H:%M")
