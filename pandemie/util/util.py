"""
This file contains several useful function.
"""
import sys
import os
import datetime

TIME_FORMAT = "%Y-%m-%d--%H.%M.%S"


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
