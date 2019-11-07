from pandemie.tester import AbstractStrategy
from pandemie import operations


class Marvin1(AbstractStrategy):
    def __init__(self, silent=False):
        super().__init__(silent=silent)

    def _solve(self, json_data, server):
        if "error" in json_data:
            print(json_data["error"])
            return operations.end_round()

        cities = json_data["cities"]
        events = json_data["events"]
        points = json_data["points"]
        round = json_data["round"]
        outcome = json_data["outcome"]

        pathogens = []

        pathogens_med_developing = []
        pathogens_med_available = []

        for event in events:
            if event["type"] == "pathogenEncountered":
                pathogens.append(event["pathogen"])

        pathogens_sorted = sorted(pathogens, key=lambda p: (1.2 * score(p["infectivity"]),
                                                            1.0 * score(p["mobility"]),
                                                            1.0 * score(p["duration"]),
                                                            1.2 * score(p["lethality"])),
                                  reverse=True)

        cities_sorted_tmp = sorted(cities.items(), key=lambda c: (1.0 * score(c[1]["economy"]),
                                                              1.2 * score(c[1]["hygiene"]),
                                                              1.0 * score(c[1]["government"]),
                                                              1.2 * score(c[1]["awareness"])),
                                   reverse=False)

        cities_sorted = []

        for city in cities_sorted_tmp:
            cities_sorted.append(city[0])

        for event in events:
            if event["type"] == "medicationInDevelopment":
                pathogens_med_developing.append(event["pathogen"]["name"])
                #print("developing", event["pathogen"]["name"])

        for event in events:
            if event["type"] == "medicationAvailable":
                pathogens_med_available.append(event["pathogen"]["name"])
                #print("available", event["pathogen"]["name"])

        for event in events:
            if event["type"] == "pathogenEncountered":
                if event["pathogen"]["name"] not in pathogens_med_developing:
                    if event["pathogen"]["name"] not in pathogens_med_available:
                        if event["pathogen"]["name"] == pathogens_sorted[0]["name"]:
                            if operations.PRICES["develop_medication"]["initial"] <= points:
                                print("develop", event["pathogen"]["name"])
                                return operations.develop_medication(event["pathogen"]["name"])

        city_pathogens = {}

        for city in cities.items():
            city_pathogens[city[0]] = []
            if "events" in city[1]:
                for event in city[1]["events"]:
                    if event["type"] == "outbreak":
                        city_pathogens[city[0]].append(event["pathogen"]["name"])

        for pathogen in pathogens_med_available:
            possible_cities = []
            for city, pathogens in city_pathogens.items():
                if pathogen in pathogens:
                    possible_cities.append(city)
            for city in cities_sorted:
                if city in possible_cities:
                    if operations.PRICES["deploy_medication"]["initial"] <= points:
                        print("deploy", pathogen)
                        return operations.deploy_medication(pathogen, city)

        print("round:", round, "points:", points, "outcome:", outcome)

        stats = False
        if stats:
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
            if score(value["hygiene"]) == 1:
                return operations.apply_hygienic_measures(key)

        for key, value in sorted(cities.items(), key=lambda item: score(item[1]["awareness"])):
            if score(value["awareness"]) == 1:
                return operations.launch_campaign(key)

        for key, value in sorted(cities.items(), key=lambda item: score(item[1]["government"])):
            if score(value["government"]) == 1:
                return operations.call_elections(key)

        for key, value in sorted(cities.items(), key=lambda item: score(item[1]["economy"])):
            if score(value["economy"]) == 1:
                return operations.exert_influence(key)

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
