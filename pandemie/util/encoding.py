import string


def filter_unicode(data):
    """
    Function to remove all non-printable characters from a string
    :param data: str: String to be analysed
    :return: String with all non-printable characters removed
    """
    return "".join(c for c in str(data) if c in string.printable)
