from contextlib import contextmanager

import locale
from datetime import datetime

__author__ = 'jan'


def parse_cfg_date(cfg_date):
    return datetime.strptime(cfg_date, "%Y-%m-%d %H:%M")


@contextmanager
def _fix_locale(prefix):
    oldloc = locale.getlocale(locale.LC_TIME)
    if not oldloc[0] == prefix:
        tried = []
        for suffx in ("", ".UTF8", ".ISO-8859-1", "@euro"):
            tried.append(prefix + suffx)
            try:
                locale.setlocale(locale.LC_TIME, prefix + suffx)
                yield
                locale.setlocale(locale.LC_TIME, oldloc)
                return
            except locale.Error:
                pass
        raise Exception("Cannot set locale with prefix %s. Tried: %s" % (prefix,
                                                                         ", ".join(tried)))
    else:
        yield


def pretty_date(date, month_name=False, show_year=False, with_weekday=False):
    """Pretty print the date

    :type date: datetime
    """
    format = ["%d."]
    if month_name:
        format.append(" %B ")
    else:
        format.append("%m.")

    if show_year:
        format.append("%Y")

    if with_weekday:
        format = ["%A, den "] + format

    with _fix_locale("de_DE"):
        pretty = date.strftime("".join(format).strip())

    return pretty
