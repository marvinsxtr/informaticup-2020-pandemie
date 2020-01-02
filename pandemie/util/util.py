"""
This file contains several useful function.
"""
import sys
import os
import datetime

TIME_FORMAT = "%Y-%m-%d--%H.%M.%S"


def normalize(ranking, target=1.0):
    """
    This function normalizes a ranking
    :param ranking: dict to normalize
    :param target: the sum of all scores in the resulting dict
    :return: normalized dict
    """
    raw = sum(ranking.values())
    factor = target / raw
    return {key: value * factor for key, value in ranking.items()}


def block_print():
    """
    Redirects the stdout to devnull to prevent any output.
    Reversible by calling `enable_print`
    :return: None
    """
    sys.stdout = open(os.devnull, 'w')


def enable_print():
    """
    Restores the stdout. Useful to revert a call to `block_print`.
    :return: None.
    """
    sys.stdout = sys.__stdout__


def to_camel_case(name):
    """
    Converts a name into its camel case equivalent.
    Example `to_camel_case` -> `ToCamelCase`
    :param name: string to be converted
    :return: camel case name
    """
    return name.title().replace("_", "")


def now():
    """
    Returns the current time.
    :return: current time
    """
    return datetime.datetime.today().strftime(TIME_FORMAT)


def map_symbol_score(symbol):
    """
    This functions translates the pathogen or city values into numerical values
    :param symbol: str: score string for a parameter
    :return: related number
    """
    mapping = "--", "-", "o", "+", "++"

    if symbol not in mapping:
        raise ValueError("Cannot map invalid symbol", symbol)

    return mapping.index(symbol) + 1
