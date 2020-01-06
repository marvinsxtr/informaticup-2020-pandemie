"""
This file handles the pre-processing of the raw json data and stores the logs in dicts.
"""

import json
import os

from collections import defaultdict

logs_path = "/logs/"

# This list has the raw game data as a list of json objects for each round
raw_json_rounds = []

# These store the preprocessed values for visualization
game_visualizations = {}

# store a dict for each round
# { lat -> latitude of cities
#   lon -> longitude of cities
#   name -> names of cities
#   flight_paths ->
#   counts -> pathogen counts
#   names -> pathogen names }
round_visualizations = []

# A list of the round files and label for full game visualization
option_labels = [{"label": "Visualize full game", "value": "game"}]

# Read file names and store them sorted
round_names = os.listdir(os.getcwd() + logs_path)
round_names.remove(".gitignore")
round_names = sorted(round_names, key=lambda item: int("".join(filter(str.isdigit, item))))


def init_rounds():
    """
    This function reads the raw json data and saves it in a list
    :return: None
    """
    path = os.getcwd()

    for number, round_name in enumerate(round_names):
        round_visualizations.append(dict())
        option_labels.append({"label": "Visualize {0}".format(round_name), "value": round_name})

        with open(path + logs_path + round_name, "r+") as f:
            raw_json_rounds.append(json.load(f))


def preprocess():
    init_rounds()

    # Preprocess rounds
    for number, json_round in enumerate(raw_json_rounds):
        preprocess_round(json_round, number)

    # Preprocess game
    preprocess_game()


def preprocess_round(json_round, number):
    # Store city positions
    round_update = defaultdict(list)

    # Pathogen pie
    pathogen_occurrence = defaultdict(lambda: 0)

    # Flight paths
    flight_connections = set()

    # Iterate over all cities
    for city in json_round["cities"].items():
        for event in city[1].get("events", ()):
            if event["type"] == "outbreak":  # there should only be one outbreak for each city
                round_update["lat"].append(city[1]["latitude"])
                round_update["lon"].append(city[1]["longitude"])
                round_update["name"].append(city[0])

                pathogen_occurrence[event["pathogen"]["name"]] += 1

                for connection in city[1]["connections"]:
                    flight_connections.add(frozenset((city[0], connection)))

    round_visualizations[number].update(round_update)

    round_visualizations[number].update({"counts": list(pathogen_occurrence.values()),
                                         "names": list(pathogen_occurrence.keys())})

    max_paths = 100
    # to many flight connections make the visualization lag

    flight_value = {}
    for city_pair in flight_connections:
        c1, c2 = city_pair
        flight_value[city_pair] = json_round["cities"][c1]["population"] + json_round["cities"][c2]["population"]

    sorted_flights = sorted(flight_value.items(), key=lambda x: x[1], reverse=True)[:max_paths]

    flight_path = []
    for (c1, c2), _ in sorted_flights:
        c1 = json_round["cities"][c1]
        c2 = json_round["cities"][c2]
        flight_path.append({"lat1": c1["latitude"], "lon1": c1["longitude"], "lat2": c2["latitude"],
                            "lon2": c2["longitude"]})

    round_visualizations[number].update({"flight_paths": flight_path})


def preprocess_game():
    # Outcome
    json_last_game = raw_json_rounds[len(raw_json_rounds) - 1]

    game_visualizations["outcome"] = json_last_game["outcome"]

    # Population
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
                p += city[1]["population"] * 1000
            y_population.append(p)
            tmp.remove(game["round"])

    game_visualizations["x_rounds"] = x_rounds
    game_visualizations["y_population"] = y_population

    # Pathogens in full game
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
