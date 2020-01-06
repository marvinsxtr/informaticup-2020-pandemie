"""
This file contains several useful function.
"""
import errno
import json
import sys
import os
import datetime

TIME_FORMAT = "%Y-%m-%d--%H.%M.%S"


def apply_weight(ranking, weight):
    """
    This function applies a weight to a ranking
    :param ranking: the ranking which the
    :param weight: weight to be applied
    :return: weighted ranking
    """
    return {k: v * weight for k, v in ranking.items()}


def create_file(path):
    """
    This function creates a file if it does not exist already
    :param path: path to file
    :return: None
    """
    if not os.path.exists(os.path.dirname(path)):
        try:
            os.makedirs(os.path.dirname(path))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise


def log_json(json_data):
    """
    This function saves the json data for each round for later use in visualization
    :param json_data: the json data of a round
    :return: None
    """
    path = "../visualization/logs/"

    # Delete files for new game
    if json_data["round"] == 1:
        rounds = os.listdir(path)

        for round_name in rounds:
            if round_name != ".gitignore":
                os.remove(path + round_name)

    name = "{0}round{1}.dat".format(path, json_data["round"])
    create_file(name)

    # Update current_round.dat
    with open(name, 'w') as outfile:
        outfile.write(json.dumps(json_data))
        outfile.flush()
        os.fsync(outfile.fileno())


def merge_ranking(*rankings):
    """
    This function merges multiple rankings together
    :param rankings: rankings to be merged
    :return: merged ranking
    """
    merged_rankings = {}
    for ranking in rankings:
        merged_rankings.update(ranking)
    return merged_rankings


def normalize_ranking(ranking):
    """
    This function normalizes a ranking to make it comparable to other rankings
    :param ranking: dict to normalize
    :return: normalized dict
    """
    raw = sum(ranking.values())
    if raw == 0:
        return ranking
    factor = len(ranking) / raw
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
