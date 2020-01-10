from collections import defaultdict
import yaml
from pandemie.util.encoding import filter_unicode


def analyse(file):
    """
    This function parses the given logfile and creates a statistic for each pathogen, how many games were lost and how
    many games were won, when the specific pathogen occurred. This statistic ist added to the end of the logfile.
    :param file: path to the logfile
    """
    # Init dict vor all known pathogens: Name: [win, loss]
    pathogens = {
        "Admiral Trips": [0, 0],
        "Azmodeus": [0, 0],
        "Coccus innocuus": [0, 0],
        "Endoictus": [0, 0],
        "Hexapox": [0, 0],
        "Influenza iutiubensis": [0, 0],
        "Methanobrevibacter colferi": [0, 0],
        "Moricillus": [0, 0],
        "N5-10": [0, 0],
        "Neurodermantotitis": [0, 0],
        "Phagum vidiianum": [0, 0],
        "Plorps": [0, 0],
        "Procrastinalgia": [0, 0],
        "Rhinonitis": [0, 0],
        "Saccharomyces cerevisiae mutans": [0, 0],
        "Shanty": [0, 0],
        "thisis": [0, 0],
        "Xenomonocythemia": [0, 0]
    }

    # Open the logfile
    with open(file, "r") as f:
        raw_data = f.read()

    # Split different games
    data = raw_data.split("$")
    for game in data:
        # Check if game was lost
        result_index = "loss" in game[:4]

        # Split the pathogens
        lines = game.split("\n")

        # Start at 1 -> first pathogen
        for j in range(1, len(lines) - 2):
            # Load the dict from string
            line = yaml.load(lines[j], Loader=yaml.FullLoader)
            pathogens[filter_unicode(line["name"]).strip()][result_index] += 1

    pathogen_table = ""
    for p in pathogens:
        pathogen_table += p

        # Add whitespaces for better view
        pathogen_table += " " * (31 - len(p))
        pathogen_table += "\t-\twins: %s - loss: %s\n" % (str(pathogens[p][0]), str(pathogens[p][1]))

    # Write the data to the end of the logfile
    with open(file, "a") as f:
        f.write("\n\n" + pathogen_table)
