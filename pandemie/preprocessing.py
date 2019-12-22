"""
This file handles the pre-processing of the raw json data and stores the results in dicts.
"""

import json
import os

# this list has the raw game data as a list of json objects for each round
raw_json_rounds = []

# these store the preprocessed values for visualization
game_visualizations = {}
round_visualizations = []

# a list of the round files and label for full game visualization
option_labels = [{'label': 'Visualize full game', 'value': 'game'}]
round_names = sorted(os.listdir(os.getcwd() + "/tester/tmp/"), key=lambda item: int(''.join(filter(str.isdigit, item))))


def init_rounds():
    # this function reads the raw json data and saves it in a list
    path = os.getcwd()
    number = 0
    for round_name in round_names:
        round_visualizations.insert(number, dict())
        option_labels.append({'label': 'Visualize {0}'.format(round_name), 'value': round_name})
        with open(path + "/tester/tmp/{0}".format(round_name), 'r+') as f:
            f.seek(0)
            raw_json_rounds.append(json.load(f))
        number += 1


def preprocess():
    init_rounds()

    # preprocess rounds
    for json_round, number in zip(raw_json_rounds, range(len(raw_json_rounds))):
        preprocess_round(json_round, number)

    # preprocess game
    preprocess_game()


def preprocess_round(json_round, number):
    # city positions
    lat = []
    lon = []
    name = []

    for city in json_round["cities"].items():
        if "events" in city[1]:
            lat.append(city[1]["latitude"])
            lon.append(city[1]["longitude"])
            name.append(city[0])

    round_visualizations[number].update({"lat": lat, "lon": lon, "name": name})

    # flight paths
    flight_paths = []
    left_over_cities = []

    for city in json_round["cities"].items():
        left_over_cities.append(city[0])

    for city in json_round["cities"].items():
        if city[0] in left_over_cities:
            if "events" in city[1]:
                for event in city[1]["events"]:
                    if event["type"] == "outbreak":
                        for connection in city[1]["connections"]:
                            other_city = json_round["cities"][connection]
                            new_connection = dict({"lat1": other_city["latitude"], "lon1": other_city["longitude"],
                                                   "lat2": city[1]["latitude"], "lon2": city[1]["longitude"]})
                            flight_paths.append(new_connection)
            left_over_cities.remove(city[0])

    round_visualizations[number].update({"flight_paths": flight_paths})

    # pathogen pie
    labels = []
    values = {}

    for city in json_round["cities"].items():
        if "events" in city[1]:
            for event in city[1]["events"]:
                if event["type"] == "outbreak":
                    pathogen = event["pathogen"]
                    if pathogen not in labels:
                        labels.append(pathogen["name"])
                        if not pathogen["name"] in values:
                            values[pathogen["name"]] = 1
                        else:
                            values[pathogen["name"]] += 1

    counts = []
    names = []

    for key, value in (values.items()):
        names.append(key)
        counts.append(value)

    round_visualizations[number].update({"counts": counts, "names": names})


def preprocess_game():
    # outcome
    json_last_game = raw_json_rounds[len(raw_json_rounds) - 1]

    game_visualizations["outcome"] = json_last_game["outcome"]

    # population
    y_population = []
    x_rounds = []
    tmp = []

    for r in range(len(raw_json_rounds) + 1):
        x_rounds.append(r)
        tmp.append(r)

    for round_number in range(len(round_names)):
        game = raw_json_rounds[round_number]
        if game["round"] in tmp:
            p = 0
            for city in game["cities"].items():
                p += city[1]["population"]
            y_population.append(p)
            tmp.remove(game["round"])

    game_visualizations["x_rounds"] = x_rounds
    game_visualizations["y_population"] = y_population

    # pathogens in full game
    pathogens = []

    for game in raw_json_rounds:
        for city in game["cities"].items():
            if "events" in city[1]:
                for event in city[1]["events"]:
                    if event["type"] == "outbreak":
                        pathogen = event["pathogen"]
                        if pathogen not in pathogens:
                            pathogens.append(pathogen["name"])

    pathogens = list(set(pathogens))

    game_visualizations["pathogens"] = pathogens

