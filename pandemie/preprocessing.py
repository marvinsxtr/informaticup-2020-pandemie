import json
import os

raw_json_rounds = []

game_visualization = {}
round_visualizations = []

option_labels = [{'label': 'Visualize full game', 'value': 'game'}]
round_names = sorted(os.listdir(os.getcwd() + "/tester/tmp/"), key=lambda item: int(''.join(filter(str.isdigit, item))))


def init_rounds():
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

    # visualize rounds
    number = 0
    for json_data in raw_json_rounds:
        # city positions
        lat = []
        lon = []
        name = []

        for city in json_data["cities"].items():
            if "events" in city[1]:
                lat.append(city[1]["latitude"])
                lon.append(city[1]["longitude"])
                name.append(city[0])

        round_visualizations[number].update({"lat": lat, "lon": lon, "name": name})

        # flight paths
        flight_paths = []
        left_over_cities = []

        for city in json_data["cities"].items():
            left_over_cities.append(city[0])

        for city in json_data["cities"].items():
            if city[0] in left_over_cities:
                if "events" in city[1]:
                    for event in city[1]["events"]:
                        if event["type"] == "outbreak":
                            for connection in city[1]["connections"]:
                                other_city = json_data["cities"][connection]
                                new_connection = dict({"lat1": other_city["latitude"], "lon1": other_city["longitude"],
                                                       "lat2": city[1]["latitude"], "lon2": city[1]["longitude"]})
                                flight_paths.append(new_connection)
                left_over_cities.remove(city[0])

        round_visualizations[number].update({"flight_paths": flight_paths})

        # pathogen pie
        labels = []
        values = {}

        for city in json_data["cities"].items():
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

        number += 1

    # visualize game
