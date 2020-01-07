import yaml
from pandemie.util.encoding import filter_unicode


def analyse(file):
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
    for d in data:
        # Check if game was lost
        if "loss" in d[:4]:
            i = 1
        else:
            i = 0
        # Split the pathogens
        lines = d.split("\n")
        # Start at 1 -> first pathogen
        for j in range(1, len(lines) - 2):
            # Load the dict from string
            line = yaml.load(lines[j], Loader=yaml.FullLoader)
            pathogens[filter_unicode(line["name"]).strip()][i] += 1

    s = ""
    for p in pathogens:
        s += p
        # Add whitespaces for better view
        for _ in range(len("Saccharomyces cerevisiae mutans") - len(p)):
            s += " "
        s += "\t-\twins: %s - loss: %s\n" % (str(pathogens[p][0]), str(pathogens[p][1]))

    # Write the data to the end of the logfile
    with open(file, "a") as f:
        f.write("\n\n" + s)
