import yaml
from pandemie.util.encoding import filter_unicode


def analyse(file):
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
    with open(file, "r") as f:
        raw_data = f.read()

    data = raw_data.split("$")
    for d in data:
        if "loss" in d[:4]:
            i = 1
        else:
            i = 0
        lines = d.split("\n")
        for j in range(1, len(lines) - 2):
            line = yaml.load(lines[j], Loader=yaml.FullLoader)
            pathogens[filter_unicode(line["name"]).strip()][i] += 1

    s = "".join(c + "\t-\twins: " + str(pathogens[c][0]) + "\t-\tloss: " + str(pathogens[c][1]) + "\n"
                for c in pathogens)
    with open(file, "a") as f:
        f.write("\n\n" + s)


    

