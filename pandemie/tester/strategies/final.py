from pandemie.tester import AbstractStrategy
from pandemie import operations


class Final(AbstractStrategy):
    def __init__(self, silent=False, visualize=False):
        super().__init__(silent=silent, visualize=visualize)

    def _solve(self, json_data, server):
        if "error" in json_data:
            print(json_data["error"])
            return operations.end_round()

        cities = json_data["cities"]
        events = json_data["events"]
        points = json_data["points"]
        round = json_data["round"]
        outcome = json_data["outcome"]

        ranking = {}

        def rank(*args, points):
            if points == 0:
                return
            if args not in ranking:
                ranking[args] = points
            else:
                ranking[args] += points

        pathogens = []
        pathogens_names = []
        pathogens_med_developing = []
        pathogens_med_available = []

        for event in events:
            if event["type"] == "pathogenEncountered":
                pathogens.append(event["pathogen"])

        for pathogen in pathogens:
            pathogens_names.append(pathogen["name"])

        for event in events:
            if event["type"] == "medicationInDevelopment":
                pathogens_med_developing.append(event["pathogen"]["name"])

        for event in events:
            if event["type"] == "medicationAvailable":
                pathogens_med_available.append(event["pathogen"]["name"])

        city_pathogens = {}

        for city in cities.items():
            city_pathogens[city[0]] = []
            if "events" in city[1]:
                for event in city[1]["events"]:
                    if event["type"] == "outbreak":
                        city_pathogens[city[0]].append(event["pathogen"]["name"])

        pathogens_sorted = sorted(pathogens, key=lambda p: (1.2 * score(p["infectivity"]),
                                                            1.0 * score(p["mobility"]),
                                                            1.0 * score(p["duration"]),
                                                            1.2 * score(p["lethality"]),
                                                            count_infected_cities(p["name"], city_pathogens)),
                                  reverse=True)

        cities_sorted_tmp = sorted(cities.items(), key=lambda c: (1.0 * score(c[1]["economy"]),
                                                                  1.2 * score(c[1]["hygiene"]),
                                                                  1.0 * score(c[1]["government"]),
                                                                  1.2 * score(c[1]["awareness"])),
                                   reverse=False)

        cities_sorted = []

        for city in cities_sorted_tmp:
            cities_sorted.append(city[0])

        pathogens_sorted_names = []

        for pathogen in pathogens_sorted:
            pathogens_sorted_names.append(pathogen["name"])

        def get_pathogen_pos(name):
            i = 0
            for pathogen in pathogens_sorted_names:
                if pathogen == name:
                    return len(pathogens_sorted_names) - i
                i += 1

        possible_pathogens = []
        for pathogen in pathogens_names:
            if pathogen not in pathogens_med_developing:
                if pathogen not in pathogens_med_available:
                    possible_pathogens.append(pathogen)

        for pathogen in pathogens_sorted_names:
            if pathogen in possible_pathogens:
                if operations.PRICES["develop_medication"]["initial"] <= points:
                    if pathogen not in pathogens_med_developing:
                        rank("develop_medication", pathogen, points=(100 * get_pathogen_pos(pathogen)))

        for pathogen in pathogens_med_available:
            possible_cities = []
            for pathogen_tmp in pathogens_med_available:
                for city, pathogens in city_pathogens.items():
                    if pathogen_tmp in pathogens:
                        possible_cities.append(city)
            for city in cities_sorted:
                if city in possible_cities:
                    if operations.PRICES["deploy_medication"]["initial"] <= points:
                        rank("deploy_medication", pathogen, city, points=(100 * get_pathogen_pos(pathogen)))

        # print(sorted(ranking.items(), key=lambda item: item[1], reverse=True))
        for key, value in sorted(ranking.items(), key=lambda item: item[1], reverse=True):
            # print("took", key, "with", value, "points")
            name, *args = key
            return operations.get(name, *args)

        return operations.get("end_round")


def score(symbols):
    if symbols == "--":
        return 1
    if symbols == "-":
        return 2
    if symbols == "o":
        return 3
    if symbols == "+":
        return 4
    if symbols == "++":
        return 5
    print("wrong symbols")


def count_infected_cities(pathogen_name, city_pathogens):
    count = 0
    for city, pathogens in city_pathogens.items():
        if pathogen_name in pathogens:
            count += 1
    return count
