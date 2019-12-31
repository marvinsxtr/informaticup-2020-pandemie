"""
This file contains several useful function.
"""
import sys
import os


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
