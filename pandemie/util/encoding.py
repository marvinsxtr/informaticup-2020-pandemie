import string


def filter_unicode(data):
    return "".join(c for c in str(data) if c in string.printable)
