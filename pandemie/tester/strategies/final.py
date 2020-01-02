"""
This is the strategy our team continuously improves to compete in the InformatiCup. Its basic principle is ranking
each possible operation and thereby picking the best choice.

Observations:
- a city can only be affected by one pathogen at a time
- it might be sufficient to sort by operation and afterwards sort the 12 best possibilities
- points for an operation are pre-paid for the required round duration
"""
import numbers

from pandemie.tester import AbstractStrategy
from pandemie import operations
from pandemie.util import normalize_ranking, merge_ranking


class Final(AbstractStrategy):
    def __init__(self, silent=False, visualize=False, weights=None):
        super().__init__(silent=silent, visualize=visualize, weights=weights)

    def _solve(self, json_data):
        from pandemie.util import map_symbol_score as score

        # check if an error has occurred
        if "error" in json_data:
            print(json_data["error"])
            return operations.end_round()

        # json objects contained in a round json file
        round_cities = json_data["cities"]
        round_global_events = json_data["events"]
        round_points = json_data["points"]
        round_number = json_data["round"]
        round_outcome = json_data["outcome"]

        # assigns a score to each tuple of the best operation for a measure
        measure_ranking = {}

        # these are the weights applied to the measure ranking which are in {1, ... ,12}
        measure_weights = {
            "end_round": 1,  # ends the current round
            "put_under_quarantine": 1,  # completely prevent spreading of pathogen
            "close_airport": 1,  # shut down connections from and to a city
            "close_connection": 1,  # shut down one connection

            "develop_vaccine": 1,  # after 6 rounds a vaccine is ready
            "deploy_vaccine": 1,  # deploy vaccine to specific city
            "develop_medication": 1,  # after 3 rounds a medication is available
            "deploy_medication": 1,  # deploy medication to specific city

            "exert_influence": 1,  # corresponds to economy city stat
            "call_elections": 1,  # corresponds to government city stat
            "apply_hygienic_measures": 1,  # corresponds to hygiene city stat
            "launch_campaign": 1,  # corresponds to awareness city stat
        }

        # change weights if they are given
        if self.weights:
            measure_weights = self.weights

        # this dict contains the rankings for concrete operations by measure
        operation_rankings = {
            "end_round": {},
            "put_under_quarantine": {},
            "close_airport": {},
            "close_connection": {},

            "develop_vaccine": {},
            "deploy_vaccine": {},
            "develop_medication": {},
            "deploy_medication": {},

            "exert_influence": {},
            "call_elections": {},
            "apply_hygienic_measures": {},
            "launch_campaign": {},
        }

        def get_best_operation():
            """
            This returns the best operation which will be the return value of the solve function
            :return: operation tuple
            """
            # normalize rankings
            for operation_name, operation_ranking in operation_rankings.items():
                operation_rankings[operation_name] = normalize_ranking(operation_ranking)
                # print(operation_rankings[operation_name])

            # get best operation for each measure
            for operation_name, operation_ranking in operation_rankings.items():
                if len(operation_ranking) > 0:
                    best_operation_for_measure = max(operation_ranking, key=lambda key: operation_ranking[key])
                    measure_ranking[best_operation_for_measure] = measure_weights[operation_name]

            # print(measure_ranking)

            # merge all rankings
            overall_ranking = merge_ranking(*operation_rankings.values())

            # sort overall ranking
            overall_ranking = dict(sorted(overall_ranking.items(), key=lambda item: item[1], reverse=True))

            # get best overall operation (out of all measures)
            # best_operation = max(measure_ranking, key=lambda key: measure_ranking[key])
            best_operation = max(overall_ranking, key=lambda key: overall_ranking[key])

            # calculate price and check if operation is possible
            rounds = 0
            for param in best_operation:
                if isinstance(param, numbers.Number):
                    rounds = param

            name, *rest = best_operation
            if rounds == 0:
                price = operations.PRICES[name]["initial"]
            else:
                price = rounds * operations.PRICES[name]["each"] + operations.PRICES[name]["initial"]

            # check if operation is affordable
            if price <= round_points:
                return operations.get(name, *rest)
            else:
                return operations.end_round()

        def rank_operation(*op_tuple, op_score):
            """
            Rank an operation tuple with a score; if it exists already, the score is added up
            :param op_tuple: tuple with params needed for an operation (example: ("deploy_medication", city, pathogen))
            :param op_score: score assigned to tuple
            :return:
            """

            # get the ranking corresponding to measure type
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
            return int((round_points - operations.PRICES[identifier]["initial"]) /
                       operations.PRICES[identifier]["each"])

        # used to convert a scale of scores (24 - 4 = 20 where 4 is the minimum points and 20 maximum)
        highest_rating = 24

        # average rating used for ranking
        avg_rating = 50

        """
        lists or dicts generated in pre-processing in order of generation
        """
        possible_operations_names = []

        pathogens = []
        pathogens_names = []

        pathogens_medication_available = []
        pathogens_medication_available_names = []

        pathogens_medication_in_development = []
        pathogens_medication_in_development_names = []

        cities = []
        cities_names = []

        cities_pathogen = {}
        cities_pathogen_name = {}

        pathogens_count_infected_cities = {}

        pathogens_scores = {}
        cities_scores = {}

        cities_pathogen_score = {}

        cities_count_flight_connections = {}

        cities_outbreak_names = []
        cities_outbreak_scores = {}

        cities_connected_cities_names = {}
        cities_combined_connected_cities_scores = {}
        cities_combined_connected_cities_difference = {}

        cities_airport_closed_names = []

        """
        pre-processing (for each list higher means more risk and 0 means none at all!)
        """
        # generate possible_operations_names including all possible operations in this round
        for op_name, op_prices in operations.PRICES.items():
            if op_prices["initial"] <= round_points:
                possible_operations_names.append(op_name)

        # generate lists for pathogen global events
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

            # if round_global_event["type"] == "economicCrisis":
            # todo: adjust weight for exert_influence

            # if round_global_event["type"] == "largeScalePanic":
            # todo: adjust weight for launch_campaign

        # put cities in a list
        cities = round_cities

        # put the city names in a list
        for city_name, _ in cities.items():
            cities_names.append(city_name)

        # connect pathogens to cities with a dict
        for city_name, city_stats in cities.items():
            if "events" in city_stats:
                for city_event in city_stats["events"]:
                    if city_event["type"] == "outbreak":
                        cities_pathogen[city_name] = city_event["pathogen"]
                        cities_pathogen_name[city_name] = city_event["pathogen"]["name"]

        # count how many cities are affected by each pathogen
        for pathogen_name in pathogens_names:
            affected_cities = 0
            for city_name in cities_names:
                if city_name in cities_pathogen_name:
                    if pathogen_name == cities_pathogen_name[city_name]:
                        affected_cities += 1
            pathogens_count_infected_cities[pathogen_name] = affected_cities

        # assign score to each pathogen (higher is more evil)
        for pathogen in pathogens:
            pathogen_score = score(pathogen["infectivity"]) + score(pathogen["mobility"]) + \
                             score(pathogen["duration"]) + score(pathogen["lethality"])
            pathogens_scores[pathogen["name"]] = pathogen_score

        # sort critical to uncritical pathogen
        pathogens_scores = dict(sorted(pathogens_scores.items(), key=lambda item: item[1], reverse=True))

        # assign score to each city (higher is riskier)
        for city_name, city_stats in cities.items():
            city_score = score(city_stats["economy"]) + score(city_stats["hygiene"]) + \
                         score(city_stats["government"]) + score(city_stats["awareness"])
            cities_scores[city_name] = highest_rating - city_score

        # sort worst to best city
        cities_scores = dict(sorted(cities_scores.items(), key=lambda item: item[1], reverse=True))

        # assign pathogen score to cities (higher score means higher risk in the city)
        for city_name in cities_names:
            pathogen_score = 0
            if city_name in cities_pathogen_name:
                pathogen_name = cities_pathogen_name[city_name]
                pathogen_score = pathogens_scores[pathogen_name]
            cities_pathogen_score[city_name] = pathogen_score

        # sort by combined pathogens score (higher to lower)
        cities_pathogen_score = dict(sorted(cities_pathogen_score.items(), key=lambda item: item[1], reverse=True))

        # count the number of flight connections for each city
        for city_name, city_stats in cities.items():
            flight_connections = 0
            for _ in city_stats["connections"]:
                flight_connections += 1
            cities_count_flight_connections[city_name] = flight_connections

        # rate the outbreak for each affected city
        for city_name, city_stats in cities.items():
            cities_outbreak_scores[city_name] = 0
            if "events" in city_stats:
                for city_event in city_stats["events"]:
                    if city_event["type"] == "outbreak":
                        cities_outbreak_names.append(city_name)
                        # this score is acquired by combining prevalence, duration and pathogen strength
                        outbreak_score = round((1 + city_event["prevalence"]) *
                                               (round_number - city_event["sinceRound"] +
                                                pathogens_scores[city_event["pathogen"]["name"]] +
                                                pathogens_count_infected_cities[city_event["pathogen"]["name"]]), 4)
                        cities_outbreak_scores[city_name] = outbreak_score

        # associate connected cities to a city
        for city_name, city_stats in cities.items():
            if "connections" in city_stats:
                cities_connected_cities_names[city_name] = city_stats["connections"]

        # combine score of connected cities
        for city_name in cities_names:
            combined_score = 0
            for connected_city_name in cities_connected_cities_names[city_name]:
                combined_score += cities_scores[connected_city_name]
            cities_combined_connected_cities_scores[city_name] = combined_score

        # sort higher to lower
        cities_combined_connected_cities_scores = dict(sorted(cities_combined_connected_cities_scores.items(),
                                                              key=lambda item: item[1], reverse=True))

        # calculate difference of city score to its connected cities scores
        for city_name, combined_score in cities_combined_connected_cities_scores.items():
            difference = 0
            if combined_score != 0:
                difference = round(abs(cities_scores[city_name] - combined_score / len(
                    cities_connected_cities_names[city_name])), 5)
            cities_combined_connected_cities_difference[city_name] = difference

        # sort higher to lower
        cities_combined_connected_cities_difference = dict(sorted(cities_combined_connected_cities_difference.items(),
                                                                  key=lambda item: item[1], reverse=True))

        # make a list of closed airport cities
        for city_name, city_stats in cities.items():
            if "events" in city_stats:
                for event in city_stats["events"]:
                    if event["type"] == "airportClosed":
                        cities_airport_closed_names.append(city_name)

        """
        rank the operations for each measure based on collected data
        """
        # put cities most at risk under quarantine
        for city_name in cities_names:
            maximum = affordable_rounds("put_under_quarantine")
            if maximum >= 1:
                rank_operation("put_under_quarantine", city_name, maximum, op_score=round(
                    measure_weights["put_under_quarantine"] * (
                        cities_pathogen_score[city_name] +
                        cities_scores[city_name] +
                        cities_outbreak_scores[city_name] +
                        cities_count_flight_connections[city_name]), 5))

        # develop medication for most dangerous pathogens
        for pathogen_name in pathogens_names:
            if pathogen_name not in pathogens_medication_available_names and pathogen_name not in \
                    pathogens_medication_in_development_names:
                rank_operation("develop_medication", pathogen_name, op_score=round(
                    measure_weights["develop_medication"] * (
                        pathogens_scores[pathogen_name] +
                        pathogens_count_infected_cities[pathogen_name]), 5))

        # deploy medication in cities at most risk
        for city_name, pathogen_name in cities_pathogen_name.items():
            if pathogen_name in pathogens_medication_available_names:
                rank_operation("deploy_medication", pathogen_name, city_name, op_score=round(
                    measure_weights["deploy_medication"] * (
                        cities_pathogen_score[city_name] +
                        cities_scores[city_name] +
                        cities_outbreak_scores[city_name] +
                        cities_count_flight_connections[city_name] +
                        pathogens_scores[pathogen_name] +
                        pathogens_count_infected_cities[pathogen_name]), 5))

        # close airports with most difference in risk compared to connected cities
        for city_name in cities_names:
            if city_name not in cities_airport_closed_names:
                maximum = affordable_rounds("close_airport")
                if maximum >= 1:
                    rank_operation("close_airport", city_name, maximum, op_score=round(
                        measure_weights["close_airport"] * (
                            cities_combined_connected_cities_difference[city_name] +
                            cities_combined_connected_cities_scores[city_name]), 5))

        # use collected data to make a decision
        return get_best_operation()
