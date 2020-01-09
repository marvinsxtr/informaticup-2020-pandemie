"""
This is the strategy our team continuously improves to compete in the InformatiCup. Its basic principle is ranking
each possible operation and thereby picking the best choice.

Observations:
- a city can only be affected by one pathogen at a time
- it might be sufficient to sort by operation and afterwards sort the 12 best possibilities
- points for an operation are pre-paid for the required round duration
"""
import random

from pandemie.tester import AbstractStrategy
from pandemie.util import normalize_ranking, merge_ranking, operations, map_symbol_score
from pandemie.util import map_symbol_score as score, apply_weight


class Final1(AbstractStrategy):
    def __init__(self, silent=False, visualize=False, weights=None):
        super().__init__(silent=silent, visualize=visualize, weights=weights)

    def _solve(self, json_data):

        # Check if an error has occurred
        if "error" in json_data:
            print(json_data["error"])
            return operations.end_round()

        # Json objects contained in a round json file
        round_cities = json_data["cities"]
        round_global_events = json_data["events"]
        round_points = json_data["points"]
        round_number = json_data["round"]
        round_outcome = json_data["outcome"]

        # Assigns a score to each tuple of the best operation for a measure
        measure_ranking = {}

        # Change weights if they are given
        if self.weights:
            measure_weights = self.weights
        else:
            # These are the weights applied to the measure ranking
            measure_weights = {
                "end_round": 1,  # Ends the current round
                "put_under_quarantine": 0.05,  # Completely prevent spreading of pathogen
                "close_airport": 0.1,  # Shut down connections from and to a city
                "close_connection": 0.1,  # Shut down one connection

                "develop_vaccine": 0.8,  # After 6 rounds a vaccine is ready
                "deploy_vaccine": 1,  # Deploy vaccine to specific city
                "develop_medication": 0.9,  # After 3 rounds a medication is available
                "deploy_medication": 1,  # Deploy medication to specific city

                "exert_influence": 1,  # Corresponds to economy city stat
                "call_elections": 1,  # Corresponds to government city stat
                "apply_hygienic_measures": 1,  # Corresponds to hygiene city stat
                "launch_campaign": 1,  # Corresponds to awareness city stat
            }

        # This dict contains the rankings for concrete operations by measure
        operation_rankings = {op: {} for op in operations.OPERATIONS}

        def is_affordable(identifier):
            """
            This function returns whether a measure is affordable
            :param identifier: operation name
            :return: whether the measure is affordable
            """
            if round_points == 0:
                return False
            return round_points - operations.PRICES[identifier]["initial"] >= 0

        def get_best_operation():
            """
            This returns the best operation which will be the return value of the solve function
            :return: operation tuple
            """
            # Normalize and weight rankings
            for operation_name in operation_rankings.keys():
                operation_rankings[operation_name] = normalize_ranking(operation_rankings[operation_name])
                operation_rankings[operation_name] = apply_weight(operation_rankings[operation_name],
                                                                  measure_weights[operation_name])

            # Get best operation for each measure
            for operation_name, operation_ranking in operation_rankings.items():
                if len(operation_ranking) > 0:
                    best_operation_for_measure = max(operation_ranking, key=lambda key: operation_ranking[key])
                    measure_ranking[best_operation_for_measure] = measure_weights[operation_name]

            # Merge all rankings
            overall_ranking = merge_ranking(*operation_rankings.values())

            # Sort overall ranking
            overall_ranking = dict(sorted(overall_ranking.items(), key=lambda item: item[1], reverse=True))

            # print(list(overall_ranking.items()))

            # Check if ranking is empty
            if len(overall_ranking) == 0:
                print("No Ranking!!!")
                return operations.end_round()

            # Get best overall operation (out of all measures):
            # This picks a random operation out of the best 12 operations (for each measure)
            # best_operation = random.choice(list(measure_ranking.keys()))

            # This picks the operation with the max score in the overall merged ranking
            best_operation = max(overall_ranking, key=lambda key: overall_ranking[key])

            if not is_affordable(best_operation[0]):
                # print("Save Money! (%s) %i" % (str(best_operation), int(round_points)))
                return operations.end_round()

            name, *args = best_operation
            # print(name, round_points)
            return operations.get(name, *args)

        def rank_operation(*op_tuple, op_score):
            """
            Rank an operation tuple with a score; if it exists already, the score is added up
            :param op_tuple: tuple with params needed for an operation (example: ("deploy_medication", city, pathogen))
            :param op_score: score assigned to tuple
            :return: None
            """
            # Get the ranking corresponding to measure type
            name, *_ = op_tuple
            operation_ranking = operation_rankings[name]

            if op_score == 0:
                return
            if op_tuple not in operation_ranking:
                operation_ranking[op_tuple] = op_score
            else:
                operation_ranking[op_tuple] += op_score

        def affordable_rounds(identifier):
            """
            This function calculates the maximal number of rounds affordable for an operation
            :param identifier: operation name
            :return: max duration in rounds
            """
            if round_points == 0:
                return 0
            return int((round_points - operations.PRICES[identifier]["initial"]) /
                       operations.PRICES[identifier]["each"])

        # Used to convert a scale of scores (24 - 4 = 20 where 4 is the minimum points and 20 maximum)
        highest_rating = 24

        """
        lists or dicts generated in pre-processing in order of generation
        """
        pathogens = []
        pathogens_names = []

        pathogens_medication_available = []
        pathogens_medication_available_names = []

        pathogens_medication_in_development = []
        pathogens_medication_in_development_names = []

        pathogens_vaccine_in_development = []
        pathogens_vaccine_in_development_names = []

        pathogens_vaccine_available = []
        pathogens_vaccine_available_names = []

        cities = []
        cities_names = []

        cities_pathogen = {}
        cities_pathogen_name = {}

        cities_awareness_score = {}
        cities_government_score = {}
        cities_hygiene_score = {}
        cities_economy_score = {}

        pathogens_count_infected_cities = {}

        pathogens_scores = {}
        cities_scores = {}

        cities_pathogen_score = {}

        cities_count_flight_connections = {}

        outbreak_city_names = []
        cities_outbreak_scores = {}
        cities_outbreak = {}

        cities_connected_cities_names = {}
        cities_combined_connected_cities_scores = {}
        cities_combined_connected_cities_difference = {}

        cities_airport_closed_names = []

        flight_connections = set()
        flight_connections_closed = set()
        flight_connections_one_infected = []
        flight_connections_one_infected_score = {}

        """
        pre-processing (for each list higher means more risk and 0 means none at all!)
        """

        # Generate lists for pathogen global events
        for round_global_event in round_global_events:
            if round_global_event["type"] == "pathogenEncountered":
                pathogens.append(round_global_event["pathogen"])
                pathogens_names.append(round_global_event["pathogen"]["name"])

            if round_global_event["type"] == "medicationAvailable":
                pathogens_medication_available.append(round_global_event["pathogen"])
                pathogens_medication_available_names.append(round_global_event["pathogen"]["name"])

            if round_global_event["type"] == "medicationInDevelopment":
                pathogens_medication_in_development.append(round_global_event["pathogen"])
                pathogens_medication_in_development_names.append(round_global_event["pathogen"]["name"])

            if round_global_event["type"] == "vaccineAvailable":
                pathogens_vaccine_available.append(round_global_event["pathogen"])
                pathogens_vaccine_available_names.append(round_global_event["pathogen"]["name"])

            if round_global_event["type"] == "vaccineInDevelopment":
                pathogens_vaccine_in_development.append(round_global_event["pathogen"])
                pathogens_vaccine_in_development_names.append(round_global_event["pathogen"]["name"])

            if round_global_event["type"] == "economicCrisis":
                measure_weights["exert_influence"] *= 1.2

            if round_global_event["type"] == "largeScalePanic":
                measure_weights["launch_campaign"] *= 1.2

        # Put cities in a list
        cities = round_cities

        # Assign score to each city (higher is riskier)
        for city_name, city_stats in cities.items():
            city_score = score(city_stats["economy"]) + score(city_stats["hygiene"]) + score(
                city_stats["government"]) + score(city_stats["awareness"])
            cities_scores[city_name] = highest_rating - city_score

        # Assign score to each pathogen (higher is more evil)
        for pathogen in pathogens:
            pathogen_score = score(pathogen["infectivity"]) + score(pathogen["mobility"]) + \
                             score(pathogen["duration"]) + score(pathogen["lethality"])
            pathogens_scores[pathogen["name"]] = pathogen_score

        # Count how many cities are affected by each pathogen
        for pathogen_name in pathogens_names:
            affected_cities = 0
            for city_name in cities_names:
                if city_name in cities_pathogen_name:
                    if pathogen_name == cities_pathogen_name[city_name]:
                        affected_cities += 1
            pathogens_count_infected_cities[pathogen_name] = affected_cities

        # Generate dicts mapping cities to values
        for city_name, city_stats in cities.items():

            # Put the city names in a list
            cities_names.append(city_name)

            # Get scores for city stats
            cities_hygiene_score[city_name] = city_stats["hygiene"]
            cities_awareness_score[city_name] = city_stats["awareness"]
            cities_economy_score[city_name] = city_stats["economy"]
            cities_government_score[city_name] = city_stats["government"]

            # Assign pathogen score to cities (higher score means higher risk in the city)
            pathogen_score = 0
            if city_name in cities_pathogen_name:
                pathogen_name = cities_pathogen_name[city_name]
                pathogen_score = pathogens_scores[pathogen_name]
            cities_pathogen_score[city_name] = pathogen_score

            # Count the number of flight connections for each city
            count_flight_connections = 0
            for _ in city_stats["connections"]:
                count_flight_connections += 1
            cities_count_flight_connections[city_name] = count_flight_connections

            # Associate connected cities to a city
            if "connections" in city_stats:
                cities_connected_cities_names[city_name] = city_stats["connections"]

            # Combine score of connected cities
            combined_score = 0
            for connected_city_name in cities_connected_cities_names[city_name]:
                combined_score += cities_scores[connected_city_name]
            cities_combined_connected_cities_scores[city_name] = combined_score

            # Rate the outbreak for each affected city
            cities_outbreak_scores[city_name] = 0
            if "events" in city_stats:
                for city_event in city_stats["events"]:

                    # Make a list of closed airport cities
                    if city_event["type"] == "airportClosed":
                        cities_airport_closed_names.append(city_name)

                    # Collect closed connections
                    if city_event["type"] == "connectionClosed":
                        flight_connections_closed.add(frozenset((city_name, city_event["city"])))

                    # Collect connected cities in a set
                    connections = city_stats["connections"]
                    for connected_city_name in connections:
                        flight_connections.add(frozenset((city_name, connected_city_name)))

                    # Generate outbreak related dicts
                    if city_event["type"] == "outbreak":
                        # Assign the name of the pathogen in each city
                        cities_pathogen[city_name] = city_event["pathogen"]
                        cities_pathogen_name[city_name] = city_event["pathogen"]["name"]

                        outbreak_city_names.append(city_name)
                        cities_outbreak[city_name] = city_event

                        # This score is acquired by combining prevalence, duration and pathogen strength
                        outbreak_score = round((1 + city_event["prevalence"]) *
                                               (round_number - city_event["sinceRound"] +
                                                city_stats["population"]) +
                                               pathogens_scores[city_event["pathogen"]["name"]] +
                                               pathogens_count_infected_cities[city_event["pathogen"]["name"]], 5)
                        cities_outbreak_scores[city_name] = outbreak_score

        # Calculate difference of city score to its connected cities scores
        for city_name, combined_score in cities_combined_connected_cities_scores.items():
            difference = 0
            if combined_score != 0:
                difference = round(abs(cities_scores[city_name] - combined_score / len(
                    cities_connected_cities_names[city_name])), 5)
            cities_combined_connected_cities_difference[city_name] = difference

        # Rank connections by comparing their outbreaks
        for flight_connection in flight_connections:
            connection = tuple(flight_connection)
            x, y = tuple(flight_connection)

            x_infected = x in outbreak_city_names
            y_infected = y in outbreak_city_names

            # Check if only one city in the connection is infected
            if x_infected ^ y_infected:
                flight_connections_one_infected.append(connection)

                # Assign a score to the connection
                if x_infected:
                    infected_city = x
                else:
                    infected_city = y

                flight_connections_one_infected_score[connection] = \
                    cities[infected_city]["population"] * cities_outbreak[infected_city]["prevalence"] + \
                    cities_pathogen_score[infected_city]

        """
        rank the operations for each measure based on collected data
        """
        # Put cities most at risk under quarantine
        for city_name in cities_names:
            maximum = affordable_rounds("put_under_quarantine")
            if maximum >= 1:
                rank_operation("put_under_quarantine", city_name, maximum, op_score=round(
                    measure_weights["put_under_quarantine"] * (
                            cities_pathogen_score[city_name] +
                            cities_scores[city_name] +
                            cities_outbreak_scores[city_name] +
                            (1 / operations.PRICES["put_under_quarantine"]["initial"]) +
                            cities_count_flight_connections[city_name] / 100), 5))

        # Develop medication for most dangerous pathogens
        for pathogen_name in pathogens_names:
            if pathogen_name not in pathogens_medication_available_names and pathogen_name not in \
                    pathogens_medication_in_development_names:
                # if is_affordable("develop_medication"):
                    rank_operation("develop_medication", pathogen_name, op_score=round(
                        measure_weights["develop_medication"] * (
                                pathogens_scores[pathogen_name] +
                                1 / operations.PRICES["develop_medication"]["initial"] * 10 +
                                pathogens_count_infected_cities[pathogen_name]), 5))

        # Deploy medication in cities at most risk
        for city_name, pathogen_name in cities_pathogen_name.items():
            if pathogen_name in pathogens_medication_available_names:
                # if is_affordable("deploy_medication"):
                    rank_operation("deploy_medication", pathogen_name, city_name, op_score=round(
                        measure_weights["deploy_medication"] * (
                                cities_pathogen_score[city_name] +
                                cities_scores[city_name] +
                                cities_outbreak_scores[city_name] +
                                cities_count_flight_connections[city_name] +
                                pathogens_scores[pathogen_name] +
                                1 / operations.PRICES["deploy_medication"]["initial"] * 10 +
                                pathogens_count_infected_cities[pathogen_name]), 5))

        # Develop vaccine for most dangerous pathogens
        for pathogen in pathogens:
            if pathogen["name"] not in pathogens_vaccine_available_names and pathogen["name"] not in \
                    pathogens_vaccine_in_development_names:
                # if is_affordable("develop_vaccine"):
                    rank_operation("develop_vaccine", pathogen["name"], op_score=round(
                        measure_weights["develop_vaccine"] * (
                                pathogens_scores[pathogen["name"]] +
                                map_symbol_score(pathogen["lethality"]) * 5 +
                                1 / operations.PRICES["develop_vaccine"]["initial"] * 10 +
                                pathogens_count_infected_cities[pathogen["name"]]), 5))

        # Deploy vaccine in cities at most risk
        for city_name, pathogen_name in cities_pathogen_name.items():
            if pathogen_name in pathogens_vaccine_available_names:
                # if is_affordable("deploy_vaccine"):
                    rank_operation("deploy_vaccine", pathogen_name, city_name, op_score=round(
                        measure_weights["deploy_vaccine"] * (
                                cities_pathogen_score[city_name] +
                                cities_scores[city_name] +
                                cities_outbreak_scores[city_name] +
                                cities_count_flight_connections[city_name] +
                                pathogens_scores[pathogen_name] +
                                1 / operations.PRICES["deploy_vaccine"]["initial"] * 10 +
                                pathogens_count_infected_cities[pathogen_name]), 5))

        # Close airports with most difference in risk compared to connected cities
        for city_name in cities_names:
            if city_name not in cities_airport_closed_names and city_name in outbreak_city_names:
                maximum = affordable_rounds("close_airport")
                if maximum >= 1:
                    rank_operation("close_airport", city_name, maximum, op_score=round(
                        measure_weights["close_airport"] * (
                                cities_combined_connected_cities_difference[city_name] +
                                cities_combined_connected_cities_scores[city_name] +
                                cities_outbreak_scores[city_name] +
                                1 / operations.PRICES["close_airport"]["initial"] * 10 +
                                cities_pathogen_score[city_name]), 5))

        # Close connections based on the difference between two cities
        for connection in flight_connections_one_infected:
            if frozenset(connection) not in flight_connections_closed:
                x, y = connection
                maximum = affordable_rounds("close_connection")
                if maximum >= 1:
                    rank_operation("close_connection", x, y, maximum, op_score=round(
                        measure_weights["close_connection"] * (
                            1 / operations.PRICES["close_connection"]["initial"] * 10 +
                            flight_connections_one_infected_score[connection]), 5))

        # Use collected data to make a decision
        return get_best_operation()
