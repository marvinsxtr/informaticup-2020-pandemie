"""
This is the strategy our team continuously improves to compete in the InformatiCup. Its basic principle is ranking
each possible operation and thereby picking the best choice.

Observations:
- more efficient to put uninfected cities under quarantine
"""

from pandemie.tester import AbstractStrategy
from pandemie import operations


class Final(AbstractStrategy):
    def __init__(self, silent=False, visualize=False):
        super().__init__(silent=silent, visualize=visualize)

    def _solve(self, json_data, server):
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

        # assigns each tuple of an operation a score
        ranking = {}

        # these are the weights/multipliers applied to each possible operation
        end_round_weight = 1  # ends the current round
        put_under_quarantine_weight = 1  # completely prevent spreading of pathogen
        close_airport_weight = 1  # shut down connections from and to a city
        close_connection_weight = 1  # shut down one connection

        develop_vaccine_weight = 1  # after 6 rounds a vaccine is ready
        deploy_vaccine_weight = 1  # deploy vaccine to specific city
        develop_medication_weight = 1  # after 3 rounds a medication is available
        deploy_medication_weight = 1  # deploy medication to specific city

        exert_influence_weight = 1  # corresponds to economy city stat
        call_elections_weight = 1  # corresponds to government city stat
        apply_hygienic_measures_weight = 1  # corresponds to hygiene city stat
        launch_campaign_weight = 1  # corresponds to awareness city stat

        def rank_operation(*op_tuple, op_score):
            """
            Rank an operation tuple with a score; if it exists already, the score is added up
            :param op_tuple: tuple with params needed for an operation (example: ("deploy_medication", city, pathogen))
            :param op_score: score assigned to tuple
            :return:
            """
            if op_score == 0:
                return
            if op_tuple not in ranking:
                ranking[op_tuple] = op_score
            else:
                ranking[op_tuple] += op_score

        def score(symbols):
            """
            This functions translates the pathogen values into numerical values
            :param symbols: str: score string for a parameter
            :return: related number
            """
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
            print("Wrong symbols")

        # used to convert a scale of scores (24 - 4 = 20 where 4 is the minimum points and 20 maximum)
        highest_rating = 24

        """
        lists or dicts generated in pre-processing in order of generation
        """
        possible_operations_names = []

        pathogens = []
        pathogens_names = []

        cities = []
        cities_names = []

        pathogens_medication_available = []
        pathogens_medication_available_names = []

        pathogens_medication_in_development = []
        pathogens_medication_in_development_names = []

        city_pathogens = {}
        city_pathogens_names = {}

        pathogens_count_infected_cities = {}

        pathogens_scores = {}
        cities_scores = {}

        cities_combined_pathogens_score = {}

        cities_count_flight_connections = {}

        cities_outbreak_scores = {}

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
            city_pathogens[city_name] = []
            city_pathogens_names[city_name] = []
            if "events" in city_stats:
                for city_event in city_stats["events"]:
                    if city_event["type"] == "outbreak":
                        city_pathogens[city_name].append(city_event["pathogen"])
                        city_pathogens_names[city_name].append(city_event["pathogen"]["name"])

        # count how many cities are affected by each pathogen
        for pathogen_name in pathogens_names:
            affected_cities = 0
            for city_name, _ in cities.items():
                if pathogen_name in city_pathogens_names[city_name]:
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

        # combined score of city and pathogen scores (higher score means higher risk in the city)
        for city_name, city_score in cities_scores.items():
            pathogen_score = 0
            for pathogen_name in city_pathogens_names[city_name]:
                pathogen_score += pathogens_scores[pathogen_name]
            combined_score = city_score + pathogen_score
            cities_combined_pathogens_score[city_name] = combined_score

        # sort by combined pathogens score (higher to lower)
        cities_combined_pathogens_score = dict(sorted(cities_combined_pathogens_score.items(),
                                                      key=lambda item: item[1], reverse=True))

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
                        # this score is acquired by combining prevalence, duration and pathogen strength
                        outbreak_score = round((1 + city_event["prevalence"]) *
                                               (round_number - city_event["sinceRound"] +
                                                pathogens_scores[city_event["pathogen"]["name"]]), 2)
                        cities_outbreak_scores[city_name] = outbreak_score

        """
        rank the operations based on collected data
        """
        # put cities most at risk under quarantine
        for city_name in cities_names:
            rank_operation("put_under_quarantaine", city_name, 3, op_score=put_under_quarantine_weight * (
                    cities_combined_pathogens_score[city_name] +
                    cities_scores[city_name] +
                    cities_outbreak_scores[city_name] +
                    cities_count_flight_connections[city_name]))

        # sort ranking
        ranking = dict(sorted(ranking.items(), key=lambda item: item[1], reverse=True))

        # debug output for generated lists
        print_debug = False
        if print_debug:
            print(possible_operations_names)
            print(pathogens_medication_in_development_names)
            print(pathogens_medication_available_names)
            print(pathogens_names)
            print(city_pathogens_names)
            print(pathogens_count_infected_cities)
            print(pathogens_scores)
            print(cities_scores)
            print(cities_combined_pathogens_score)
            print(cities_count_flight_connections)
            print(cities_outbreak_scores)

            print(ranking)

        # iterate over ranked operations to determine action
        for operation, score in ranking.items():
            # print("took", operation, "with", score, "points")
            op_name, *op_rest = operation

            # check if need to save for required action
            # todo check if this is a good idea
            if op_name not in possible_operations_names:
                return operations.end_round()
            # check if operation can be afforded
            if op_name in possible_operations_names:
                return operations.get(op_name, *op_rest)
            else:
                continue
        return operations.end_round()
