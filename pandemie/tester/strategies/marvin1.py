from pandemie.tester import AbstractStrategy
from pandemie import operations


class Marvin1(AbstractStrategy):
    def __init__(self, silent=False, visualize=False):
        super().__init__(silent=silent, visualize=visualize)

    def _solve(self, json_data):
        if "error" in json_data:
            print(json_data["error"])
            return operations.end_round()

        cities = json_data["cities"]
        events = json_data["events"]
        points = json_data["points"]
        round = json_data["round"]
        outcome = json_data["outcome"]

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

        possible_pathogens = []
        for pathogen in pathogens_names:
            if pathogen not in pathogens_med_developing:
                if pathogen not in pathogens_med_available:
                    possible_pathogens.append(pathogen)

        for pathogen in pathogens_sorted_names:
            if pathogen in possible_pathogens:
                if operations.PRICES["develop_medication"]["initial"] <= points:
                    # print("develop", pathogen)
                    return operations.develop_medication(pathogen)

        for pathogen in pathogens_med_available:
            possible_cities = []
            for pathogen_tmp in pathogens_med_available:
                for city, pathogens in city_pathogens.items():
                    if pathogen_tmp in pathogens:
                        possible_cities.append(city)
            for city in cities_sorted:
                if city in possible_cities:
                    if operations.PRICES["deploy_medication"]["initial"] <= points:
                        # print("deploy", pathogen)
                        return operations.deploy_medication(pathogen, city)

        # print("round:", round, "points:", points, "outcome:", outcome)

        stats = False
        if stats:
            print(pathogens_med_available)
            count_events = 0
            outbreak_events = 0
            other_events = 0
            for city in cities.items():
                city_name = city[0]
                city_info = city[1]

                if "events" in city_info:
                    if len(city_info["events"]) > 0:
                        for event in city_info["events"]:
                            if event["type"] == "outbreak":
                                outbreak_events = outbreak_events + 1
                            else:
                                other_events = other_events + 1
                        count_events = count_events + 1

            print("events:", count_events, "outbreaks:", outbreak_events, "others:", other_events,
                  "cities:", len(cities))

        if points < 3:
            return operations.end_round()

        for key, value in sorted(cities.items(), key=lambda item: score(item[1]["hygiene"])):
            return operations.apply_hygienic_measures(key)

        for key, value in sorted(cities.items(), key=lambda item: score(item[1]["awareness"])):
            return operations.launch_campaign(key)

        for key, value in sorted(cities.items(), key=lambda item: score(item[1]["government"])):
            return operations.call_elections(key)

        for key, value in sorted(cities.items(), key=lambda item: score(item[1]["economy"])):
            return operations.exert_influence(key)

        print("end round")
        return operations.end_round()


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
