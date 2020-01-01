"""
This is the strategy our team continuously improves to compete in the InformatiCup. Its basic principle is ranking
each possible operation and thereby picking the best choice.

Observations:
- a city can only be affected by one pathogen at a time
"""

from pandemie.tester import AbstractStrategy
from pandemie import operations


class Final(AbstractStrategy):
    def __init__(self, silent=False, visualize=False, weights=None):
        super().__init__(silent=silent, visualize=visualize, weights=weights)

    def _solve(self, json_data, server, weights):
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
        put_under_quarantine_weight = 0.8  # completely prevent spreading of pathogen
        close_airport_weight = 0.8  # shut down connections from and to a city
        close_connection_weight = 1  # shut down one connection

        develop_vaccine_weight = 1  # after 6 rounds a vaccine is ready
        deploy_vaccine_weight = 1  # deploy vaccine to specific city
        develop_medication_weight = 1.0489695419909937  # after 3 rounds a medication is available
        deploy_medication_weight = 1.0204341548464462  # deploy medication to specific city

        exert_influence_weight = 1  # corresponds to economy city stat
        call_elections_weight = 1  # corresponds to government city stat
        apply_hygienic_measures_weight = 1  # corresponds to hygiene city stat
        launch_campaign_weight = 1  # corresponds to awareness city stat

        # unpack weights if they are given
        if weights:
            put_under_quarantine_weight, develop_medication_weight, deploy_medication_weight, close_airport_weight = \
                weights

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
            This functions translates the pathogen or city values into numerical values
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

        def max_rounds(identifier):
            """
            This function calculates the maximum duration in rounds which an operation can last with the current points
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
        rank the operations based on collected data (for each operation, the following steps are taken:)
            - make score comparable to other operations
            - adjust weight
            - rank operations
        """
        # add up scores to get avg for put_under_quarantaine
        put_under_quarantine_overall_scores = []
        for city_name in cities_names:
            put_under_quarantine_overall_scores.append(
                    cities_pathogen_score[city_name] +
                    cities_scores[city_name] +
                    cities_outbreak_scores[city_name] +
                    cities_count_flight_connections[city_name])
        put_under_quarantine_overall_scores_avg = sum(put_under_quarantine_overall_scores) / len(
            put_under_quarantine_overall_scores)

        # calculate weight
        if put_under_quarantine_overall_scores_avg != 0:
            put_under_quarantine_weight *= round(avg_rating / put_under_quarantine_overall_scores_avg, 5)

        # put cities most at risk under quarantine
        for city_name in cities_names:
            maximum = max_rounds("put_under_quarantine")
            if maximum >= 1:
                rank_operation("put_under_quarantaine", city_name, maximum, op_score=round(
                    put_under_quarantine_weight * (
                        cities_pathogen_score[city_name] +
                        cities_scores[city_name] +
                        cities_outbreak_scores[city_name] +
                        cities_count_flight_connections[city_name]), 5))

        # add up scores to get avg for develop_medication
        develop_medication_overall_scores = []
        for pathogen_name in pathogens_names:
            develop_medication_overall_scores.append(
                pathogens_scores[pathogen_name] +
                pathogens_count_infected_cities[pathogen_name])
        develop_medication_overall_scores_avg = sum(develop_medication_overall_scores) / len(
            develop_medication_overall_scores)

        # calculate weight
        if develop_medication_overall_scores_avg != 0:
            develop_medication_weight *= round(avg_rating / develop_medication_overall_scores_avg, 5)

        # develop medication for most dangerous pathogens
        for pathogen_name in pathogens_names:
            if pathogen_name not in pathogens_medication_available_names and pathogen_name not in \
                    pathogens_medication_in_development_names:
                rank_operation("develop_medication", pathogen_name, op_score=round(
                    develop_medication_weight * (
                        pathogens_scores[pathogen_name] +
                        pathogens_count_infected_cities[pathogen_name]), 5))

        # add up scores to get avg for deploy_medication
        deploy_medication_overall_scores = []
        for city_name, pathogen_name in cities_pathogen_name.items():
            if pathogen_name in pathogens_medication_available_names:
                deploy_medication_overall_scores.append(
                    cities_pathogen_score[city_name] +
                    cities_scores[city_name] +
                    cities_outbreak_scores[city_name] +
                    cities_count_flight_connections[city_name] +
                    pathogens_scores[pathogen_name] +
                    pathogens_count_infected_cities[pathogen_name])
        deploy_medication_overall_scores_avg = 0
        if len(deploy_medication_overall_scores) != 0:
            deploy_medication_overall_scores_avg = sum(deploy_medication_overall_scores) / len(
                deploy_medication_overall_scores)

        # calculate weight
        if deploy_medication_overall_scores_avg != 0:
            deploy_medication_weight *= round(avg_rating / deploy_medication_overall_scores_avg, 5)

        # deploy medication in cities at most risk
        for city_name, pathogen_name in cities_pathogen_name.items():
            if pathogen_name in pathogens_medication_available_names:
                rank_operation("deploy_medication", pathogen_name, city_name, op_score=round(
                    deploy_medication_weight*(
                        cities_pathogen_score[city_name] +
                        cities_scores[city_name] +
                        cities_outbreak_scores[city_name] +
                        cities_count_flight_connections[city_name] +
                        pathogens_scores[pathogen_name] +
                        pathogens_count_infected_cities[pathogen_name]), 5))

        # add up scores to get avg for close_airport
        close_airport_overall_scores = []
        for city_name in cities_names:
            if city_name not in cities_airport_closed_names:
                close_airport_overall_scores.append(
                    cities_combined_connected_cities_difference[city_name] +
                    cities_combined_connected_cities_scores[city_name])
        close_airport_overall_scores_avg = sum(close_airport_overall_scores) / len(
                close_airport_overall_scores)

        # calculate weight
        if close_airport_overall_scores_avg != 0:
            close_airport_weight *= round(avg_rating / close_airport_overall_scores_avg, 5)

        # close airports with most difference in risk compared to connected cities
        for city_name in cities_names:
            if city_name not in cities_airport_closed_names:
                maximum = max_rounds("close_airport")
                if maximum >= 1:
                    rank_operation("close_airport", city_name, maximum, op_score=round(
                        close_airport_weight * (
                            cities_combined_connected_cities_difference[city_name] +
                            cities_combined_connected_cities_scores[city_name]), 5))

        # sort ranking
        ranking = dict(sorted(ranking.items(), key=lambda item: item[1], reverse=True))

        # debug output for generated lists
        print_debug = False
        if print_debug:
            print(possible_operations_names)
            print(pathogens_medication_in_development_names)
            print(pathogens_medication_available_names)
            print(pathogens_names)
            print(cities_pathogen_name)
            print(pathogens_count_infected_cities)
            print(pathogens_scores)
            print(cities_scores)
            print(cities_pathogen_score)
            print(cities_count_flight_connections)
            print(cities_outbreak_scores)

            print(ranking)

        # iterate over ranked operations to determine action
        for operation, score in ranking.items():
            op_name, *op_rest = operation

            # check if need to save for required action
            # todo check if this is a good idea and test other saving methods
            if op_name not in possible_operations_names:
                return operations.end_round()
            # check if operation can be afforded
            if op_name in possible_operations_names:
                # print("took", operation, "with", score, "points")
                return operations.get(op_name, *op_rest)
            else:
                continue
        return operations.end_round()
