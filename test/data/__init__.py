import os


def get_path(datafile):
    thisfile = os.path.abspath(os.path.expanduser(__file__))
    return os.path.join(os.path.dirname(thisfile), datafile)