import locale
from datetime import datetime

__author__ = 'jan'


def parse_cfg_date(cfg_date):
    return datetime.strptime(cfg_date, "%Y-%m-%d %H:%M")


def pretty_date(date, month_name=False, show_year=False):
    """

    :type date: datetime
    """
    format = ["%d."]
    if month_name:
        locale.setlocale(locale.LC_TIME, "de_DE")
        format.append(" %B ")
    else:
        format.append("%m.")

    if show_year:
        format.append("%Y")

    return date.strftime("".join(format).strip())
