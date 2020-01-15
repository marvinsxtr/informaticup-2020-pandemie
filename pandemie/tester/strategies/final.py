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
from pandemie.util import normalize_ranking, merge_ranking, operations, apply_weight, weighted_choice
from pandemie.util import map_symbol_score as score


class Final(AbstractStrategy):
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
                "put_under_quarantine": 30,  # Completely prevent spreading of pathogen
                "close_airport": 60,  # Shut down connections from and to a city
                "close_connection": 25,  # Shut down one connection

                "develop_vaccine": 100,  # After 6 rounds a vaccine is ready
                "deploy_vaccine": 150,  # Deploy vaccine to specific city
                "develop_medication": 100,  # After 3 rounds a medication is available
                "deploy_medication": 100,  # Deploy medication to specific city

                "exert_influence": 10,  # Corresponds to economy city stat
                "call_elections": 10,  # Corresponds to government city stat
                "apply_hygienic_measures": 10,  # Corresponds to hygiene city stat
                "launch_campaign": 10,  # Corresponds to awareness city stat
            }

        # This dict contains the rankings for concrete operations by measure
        operation_rankings = {op: {} for op in operations.OPERATIONS}

        # Measure threshold to be considered
        measure_thresholds = {
            "end_round": 1,  # Ends the current round
            "put_under_quarantine": 50,  # Completely prevent spreading of pathogen
            "close_airport": 100,  # Shut down connections from and to a city
            "close_connection": 16,  # Shut down one connection

            "develop_vaccine": 100,  # After 6 rounds a vaccine is ready
            "deploy_vaccine": 50,  # Deploy vaccine to specific city
            "develop_medication": 100,  # After 3 rounds a medication is available
            "deploy_medication": 30,  # Deploy medication to specific city

            "exert_influence": 1,  # Corresponds to economy city stat
            "call_elections": 1,  # Corresponds to government city stat
            "apply_hygienic_measures": 1,  # Corresponds to hygiene city stat
            "launch_campaign": 1,  # Corresponds to awareness city stat
        }

        # Used to convert a scale of scores (24 - 4 = 20 where 4 is the minimum points and 20 maximum)
        highest_overall_score = 24
        highest_individual_score = 6

        """
        lists or dicts generated in pre-processing
        """
        global_events_names = []

        pathogens = []
        pathogens_names = []

        pathogens_medication_available_names = []
        pathogens_medication_in_development_names = []
        pathogens_vaccine_in_development_names = []
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
        cities_outbreak_scores = {}
        cities_pathogen_score = {}

        cities_count_flight_connections = {}
        cities_outbreak = {}

        outbreak_city_names = []
        quarantine_city_names = []
        cities_airport_closed_names = []

        cities_connected_cities_names = {}
        cities_combined_connected_cities_scores = {}
        cities_combined_connected_cities_difference = {}

        flight_connections = set()
        flight_connections_closed = set()
        flight_connections_one_infected = []
        flight_connections_one_infected_score = {}

        def get_round_number(op_tuple):
            """
            This function determines the duration of the given operation
            :param op_tuple: The operation tuple
            :return: The new duration
            """
            # Unpack tuple into name and arguments
            name, *args = op_tuple

            # Calculate maximum affordable rounds
            max_rounds = affordable_rounds(name)

            # Check if operation has a duration
            if name in ("put_under_quarantine", "close_airport"):
                city, *_ = args
                if city in cities_pathogen:
                    # Get pathogen duration
                    city_pathogen = cities_pathogen[city]
                    city_duration_score = score(city_pathogen["duration"])

                    # Map the duration of the pathogen over 0 to maximal possible duration
                    city_rounds = round(((city_duration_score - 1) / 4) * max_rounds)

                    # Return calculated duration
                    return city_rounds
            elif name == "close_connection":
                from_city, to_city, *_ = args

                # Find the infected city
                if from_city in cities_pathogen:
                    city_pathogen = cities_pathogen[from_city]
                elif to_city in cities_pathogen:
                    city_pathogen = cities_pathogen[to_city]
                else:
                    # Theoretically impossible
                    return 0

                # Map duration see above
                city_duration_score = score(city_pathogen["duration"])
                city_rounds = round(((city_duration_score - 1) / 4) * max_rounds)
                return city_rounds

            # return default value
            return 0

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

            # Check if ranking is empty
            if len(overall_ranking) == 0:
                return operations.end_round()

            # Get best overall operation (out of all measures):

            # This picks a random operation out of the best 12 operations (for each measure)
            # best_operation = random.choice(list(measure_ranking.keys()))

            # This picks the operation with the max score in the overall merged ranking
            # best_operation = max(overall_ranking, key=lambda key: overall_ranking[key])

            # This picks the operation with the highest weight
            # best_operation = max(measure_ranking, key=lambda key: measure_ranking[key])

            # This picks a new best operation as long as the threshold for its score is not reached
            i = 0
            while True:
                # This picks an operation with a probability based on its weight
                best_operation = weighted_choice(measure_ranking)

                # Get the score of the operation
                name, *args, rounds = best_operation
                ranking = operation_rankings[name]
                op_score = ranking[best_operation]
                i += 1

                # Check if conditions are not met (do-while)
                if op_score >= measure_thresholds[name] or i >= len(measure_thresholds):
                    break

            # Calculate number of rounds for round based measures
            if name in ("put_under_quarantine", "close_airport", "close_connection"):
                calculated_rounds = get_round_number(best_operation)
                if calculated_rounds <= 0:
                    # End round because action was not affordable
                    return operations.end_round()
                else:
                    # Redefine best operation with adjusted rounds
                    best_operation = (name, *args, calculated_rounds)
            # Returns the best operation json
            return operations.get_operation(best_operation)

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
            rounds = int((round_points - operations.PRICES[identifier]["initial"]) /
                         operations.PRICES[identifier]["each"])
            if rounds >= 0:
                return rounds
            else:
                return 0

        def is_affordable(identifier):
            """
            This function returns whether a measure is affordable
            :param identifier: operation name
            :return: whether the measure is affordable
            """
            return round_points - operations.PRICES[identifier]["initial"] >= 0

        """
        pre-processing (for each list a higher score usually means more risk)
        """
        # Generate lists for pathogen global events
        for round_global_event in round_global_events:
            global_events_names.append(round_global_event["type"])

            if round_global_event["type"] == "pathogenEncountered":
                pathogens.append(round_global_event["pathogen"])
                pathogens_names.append(round_global_event["pathogen"]["name"])

            if round_global_event["type"] == "medicationAvailable":
                pathogens_medication_available_names.append(round_global_event["pathogen"]["name"])

            if round_global_event["type"] == "medicationInDevelopment":
                pathogens_medication_in_development_names.append(round_global_event["pathogen"]["name"])

            if round_global_event["type"] == "vaccineAvailable":
                pathogens_vaccine_available_names.append(round_global_event["pathogen"]["name"])

            if round_global_event["type"] == "vaccineInDevelopment":
                pathogens_vaccine_in_development_names.append(round_global_event["pathogen"]["name"])

        # Put cities in a list
        cities = round_cities

        # Assign score to each city (higher is riskier)
        for city_name, city_stats in cities.items():
            city_score = score(city_stats["economy"]) + score(city_stats["hygiene"]) + score(
                city_stats["government"]) + score(city_stats["awareness"])
            cities_scores[city_name] = highest_overall_score - city_score

        # Assign score to each pathogen (higher is more evil)
        for pathogen in pathogens:
            pathogen_score = score(pathogen["infectivity"]) + score(pathogen["mobility"]) + \
                             score(pathogen["duration"]) + score(pathogen["lethality"])
            pathogens_scores[pathogen["name"]] = pathogen_score

        # Generate dicts mapping cities to values
        for city_name, city_stats in cities.items():

            # Put the city names in a list
            cities_names.append(city_name)

            # Add scores for measures corresponding to city stats
            cities_awareness_score[city_name] = highest_individual_score - score(city_stats["awareness"])
            if "largeScalePanic" in global_events_names:
                cities_awareness_score[city_name] *= 2

            cities_economy_score[city_name] = highest_individual_score - score(city_stats["economy"])
            if "economicCrisis" in global_events_names:
                cities_economy_score[city_name] *= 2

            cities_hygiene_score[city_name] = highest_individual_score - score(city_stats["hygiene"])
            cities_government_score[city_name] = highest_individual_score - score(city_stats["government"])

            # Count the number of flight connections for each city
            cities_count_flight_connections[city_name] = len(city_stats["connections"])

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

                    # Collect cities under quarantine
                    if city_event["type"] == "quarantine":
                        quarantine_city_names.append(city_name)

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

                        # Map outbreak (names) to cities
                        outbreak_city_names.append(city_name)
                        cities_outbreak[city_name] = city_event

                # Assign pathogen score to cities (higher score means higher risk in the city)
                pathogen_score = 0
                if city_name in cities_pathogen_name:
                    pathogen_name = cities_pathogen_name[city_name]
                    pathogen_score = pathogens_scores[pathogen_name]
                cities_pathogen_score[city_name] = pathogen_score

        # Count how many cities are affected by each pathogen
        for pathogen_name in pathogens_names:
            affected_cities = 0
            for city_name in cities_names:
                if city_name in cities_pathogen_name:
                    if pathogen_name == cities_pathogen_name[city_name]:
                        affected_cities += 1
            pathogens_count_infected_cities[pathogen_name] = affected_cities

        for city_name, city_stats in cities.items():
            if city_name in outbreak_city_names:
                city_event = cities_outbreak[city_name]
                # This score is acquired by combining prevalence, duration and pathogen strength
                outbreak_score = round((1 + city_event["prevalence"]) *
                                       (round_number - city_event["sinceRound"] +
                                        city_stats["population"]) +
                                       pathogens_scores[city_event["pathogen"]["name"]] +
                                       pathogens_count_infected_cities[city_event["pathogen"]["name"]], 5)
                cities_outbreak_scores[city_name] = outbreak_score / 1000

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
                    cities[infected_city]["population"] * cities_outbreak[infected_city]["prevalence"] / 1000 + \
                    cities_pathogen_score[infected_city]

        """
        rank the operations for each measure based on collected data
        """
        # Put cities most at risk under quarantine
        for city_name in cities_names:
            if city_name not in quarantine_city_names and city_name in outbreak_city_names:
                overall_score = cities_pathogen_score[city_name] + \
                                cities_scores[city_name] + \
                                cities_outbreak_scores[city_name] + \
                                cities_count_flight_connections[city_name]
                """
                print(cities_pathogen_score[city_name],
                            cities_scores[city_name],
                            cities_outbreak_scores[city_name],
                            cities_count_flight_connections[city_name])
                """
                rank_operation("put_under_quarantine", city_name, 0, op_score=round(
                    measure_weights["put_under_quarantine"] * overall_score, 5))

        # Develop medication for most dangerous pathogens
        for pathogen in pathogens:
            if pathogen["name"] not in pathogens_medication_available_names and pathogen["name"] not in \
                    pathogens_medication_in_development_names:
                if is_affordable("develop_medication"):
                    overall_score = pathogens_scores[pathogen["name"]] + \
                                    score(pathogen["lethality"]) * 3 + \
                                    pathogens_count_infected_cities[pathogen["name"]]
                    """
                    print(pathogens_scores[pathogen["name"]],
                          score(pathogen["lethality"]) * 5,
                          pathogens_count_infected_cities[pathogen["name"]])
                    """
                    rank_operation("develop_medication", pathogen["name"], op_score=round(
                        measure_weights["develop_medication"] * overall_score, 5))

        # Deploy medication in cities at most risk
        for city_name, pathogen_name in cities_pathogen_name.items():
            if pathogen_name in pathogens_medication_available_names and pathogen_name not in \
                    pathogens_medication_in_development_names:
                if is_affordable("deploy_medication"):
                    overall_score = cities_pathogen_score[city_name] + \
                                    cities_scores[city_name] + \
                                    cities_outbreak_scores[city_name] * 5 + \
                                    pathogens_scores[pathogen_name]
                    """
                    print(cities_pathogen_score[city_name],
                                cities_scores[city_name],
                                cities_outbreak_scores[city_name] * 5,
                                pathogens_scores[pathogen_name])
                    """
                    rank_operation("deploy_medication", pathogen_name, city_name, op_score=round(
                        measure_weights["deploy_medication"] * overall_score, 5))

        # Develop vaccine for most dangerous pathogens
        for pathogen in pathogens:
            if pathogen["name"] not in pathogens_vaccine_available_names and pathogen["name"] not in \
                    pathogens_vaccine_in_development_names:
                if is_affordable("develop_vaccine"):
                    overall_score = pathogens_scores[pathogen["name"]] + \
                                    score(pathogen["lethality"]) * 5 + \
                                    pathogens_count_infected_cities[pathogen["name"]]
                    """
                    print(pathogens_scores[pathogen["name"]],
                                score(pathogen["lethality"]) * 5,
                                pathogens_count_infected_cities[pathogen["name"]])
                    """
                    rank_operation("develop_vaccine", pathogen["name"], op_score=round(
                        measure_weights["develop_vaccine"] * overall_score, 5))

        # Deploy vaccine in cities at most risk
        for city_name, pathogen_name in cities_pathogen_name.items():
            if pathogen_name in pathogens_vaccine_available_names:
                if is_affordable("deploy_vaccine"):
                    overall_score = cities_pathogen_score[city_name] + \
                                    cities_scores[city_name] + \
                                    cities_outbreak_scores[city_name] + \
                                    cities_count_flight_connections[city_name] + \
                                    pathogens_scores[pathogen_name] + \
                                    pathogens_count_infected_cities[pathogen_name]
                    """
                    print(cities_pathogen_score[city_name],
                                cities_scores[city_name],
                                cities_outbreak_scores[city_name],
                                cities_count_flight_connections[city_name],
                                pathogens_scores[pathogen_name],
                                pathogens_count_infected_cities[pathogen_name])
                    """
                    rank_operation("deploy_vaccine", pathogen_name, city_name, op_score=round(
                        measure_weights["deploy_vaccine"] * overall_score, 5))

        # Close airports with most difference in risk compared to connected cities
        for city_name in cities_names:
            if city_name not in cities_airport_closed_names and city_name in outbreak_city_names:
                overall_score = cities_combined_connected_cities_difference[city_name] + \
                                cities_combined_connected_cities_scores[city_name] + \
                                cities_outbreak_scores[city_name] + \
                                cities_pathogen_score[city_name]
                """
                print(cities_combined_connected_cities_difference[city_name],
                            cities_combined_connected_cities_scores[city_name],
                            cities_outbreak_scores[city_name],
                            cities_pathogen_score[city_name])
                """
                rank_operation("close_airport", city_name, 0, op_score=round(
                    measure_weights["close_airport"] * overall_score, 5))

        # Close connections based on the difference between two cities
        for connection in flight_connections_one_infected:
            if frozenset(connection) not in flight_connections_closed:
                x, y = connection
                overall_score = flight_connections_one_infected_score[connection]
                if overall_score >= 16:
                    rank_operation("close_connection", x, y, 0, op_score=round(
                        measure_weights["close_connection"] * overall_score, 5))

        # TODO: find better scoring function for these actions:
        """
        # Rank operations corresponding to city stats
        for city_name in outbreak_city_names:
            if is_affordable("apply_hygienic_measures") and cities_hygiene_score[city_name] >= 5:
                rank_operation("apply_hygienic_measures", city_name, op_score=round(
                    measure_weights["apply_hygienic_measures"] * (
                        cities_hygiene_score[city_name]), 5))

            if is_affordable("launch_campaign") and cities_awareness_score[city_name] >= 5:
                rank_operation("launch_campaign", city_name, op_score=round(
                    measure_weights["launch_campaign"] * (
                        cities_awareness_score[city_name]), 5))

            if is_affordable("exert_influence") and cities_economy_score[city_name] >= 5:
                rank_operation("exert_influence", city_name, op_score=round(
                    measure_weights["exert_influence"] * (
                        cities_economy_score[city_name]), 5))

            if is_affordable("call_elections") and cities_government_score[city_name] >= 5:
                rank_operation("call_elections", city_name, op_score=round(
                    measure_weights["call_elections"] * (
                        cities_government_score[city_name]), 5))
        """

        # Use collected data to make a decision
        return get_best_operation()
