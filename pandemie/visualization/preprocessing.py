"""
This file handles the pre-processing of the raw json data and stores the logs in dicts.
"""

import json
import os

from collections import defaultdict

logs_path = "/logs/"

# Max number of flight connections displayed
MAX_PATHS = 100

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
    This function reads the raw json data and saves it in a list.
    :return: None
    """
    path = os.getcwd()

    for number, round_name in enumerate(round_names):
        round_visualizations.append(dict())
        option_labels.append({"label": "Visualize {0}".format(round_name), "value": round_name})

        with open(path + logs_path + round_name, "r+") as f:
            raw_json_rounds.append(json.load(f))


def preprocess():
    """
    Preprocesses the whole json data.
    :return: None
    """
    # Read the files from the disk
    init_rounds()

    # Preprocess rounds
    for number, json_round in enumerate(raw_json_rounds):
        preprocess_round(json_round, number)

    # Preprocess game
    preprocess_game()


def preprocess_round(json_round, number):
    """
    Analyze a single round. Coordinates, occurring pathogens and flight connection are analyzed and store for later
    plotting.
    :param json_round: json data of the round
    :param number: index of the round visualization
    :return: None
    """
    # Store city positions
    round_update = defaultdict(list)

    # Pathogen pie
    pathogen_occurrence = defaultdict(lambda: 0)

    # Flight paths
    flight_connections = set()

    # Iterate over all cities
    for city in json_round["cities"].items():
        for event in city[1].get("events", ()):
            if event["type"] == "outbreak":  # There should only be one outbreak for each city

                # Save city coordinates
                round_update["lat"].append(city[1]["latitude"])
                round_update["lon"].append(city[1]["longitude"])
                round_update["name"].append(city[0])

                # Increase pathogen count
                pathogen_occurrence[event["pathogen"]["name"]] += 1

                # save flight connection
                for connection in city[1]["connections"]:
                    flight_connections.add(frozenset((city[0], connection)))

    # Update round visualizations
    round_visualizations[number].update(round_update)

    round_visualizations[number].update({"counts": list(pathogen_occurrence.values()),
                                         "names": list(pathogen_occurrence.keys())})

    # Calculate the `weight` of a connection by summing the population up
    flight_value = {}
    for city_pair in flight_connections:
        c1, c2 = city_pair
        flight_value[city_pair] = json_round["cities"][c1]["population"] + json_round["cities"][c2]["population"]

    # Sort flights
    sorted_flights = sorted(flight_value.items(), key=lambda x: x[1], reverse=True)[:MAX_PATHS]

    # Store connection
    flight_path = []
    for (c1, c2), _ in sorted_flights:
        c1 = json_round["cities"][c1]
        c2 = json_round["cities"][c2]
        flight_path.append({"lat1": c1["latitude"], "lon1": c1["longitude"], "lat2": c2["latitude"],
                            "lon2": c2["longitude"]})

    round_visualizations[number].update({"flight_paths": flight_path})


def preprocess_game():
    """
    Adds the occurring pathogens and the world population for each round to the game visualization.
    :return: None
    """
    # Outcome
    game_visualizations["outcome"] = raw_json_rounds[-1]["outcome"]

    # Population
    y_population = []
    x_rounds = list(range(len(raw_json_rounds)))

    # Calculating world population
    for game in raw_json_rounds:
        y_population.append(sum(city[1]["population"] for city in game["cities"].items())*1000)

    game_visualizations["x_rounds"] = x_rounds
    game_visualizations["y_population"] = y_population

    # Pathogens in full game
    pathogens = set()

    for game in raw_json_rounds:
        for city in game["cities"].items():
            for event in city[1].get("events", ()):
                if event["type"] == "outbreak":
                    pathogens.add(event["pathogen"]["name"])

    game_visualizations["pathogens"] = list(pathogens)
