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
            rank an operation tuple with a score; if it exists already, the score is added up
            :param op_tuple: tuple with params needed for an operation (example: ("deploy_medication", city, pathogen))
            :param op_score: score assigned to tuple
            :return:
            """
            if score == 0:
                return
            if op_tuple not in ranking:
                ranking[op_tuple] = op_score
            else:
                ranking[op_tuple] += op_score

        # lists or dicts generated in pre-processing in order of generation
        possible_operations_names = []

        pathogens_encountered = []
        pathogens_encountered_names = []

        pathogens_medication_available = []
        pathogens_medication_available_names = []

        pathogens_medication_in_development = []
        pathogens_medication_in_development_names = []

        city_pathogens = {}
        city_pathogens_names = {}

        pathogens_count_infected_cities = {}

        # pre-processing
        # generate possible_operations_names including all possible operations in this round
        for op_name, op_prices in operations.PRICES.items():
            if op_prices["initial"] <= round_points:
                possible_operations_names.append(op_name)

        # generate lists for pathogen global events
        for round_global_event in round_global_events:
            if round_global_event["type"] == "pathogenEncountered":
                pathogens_encountered.append(round_global_event["pathogen"])
                pathogens_encountered_names.append(round_global_event["pathogen"]["name"])

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

        # connect pathogens to cities with a dict
        for round_city_name, round_city_stats in round_cities.items():
            city_pathogens[round_city_name] = []
            city_pathogens_names[round_city_name] = []
            if "events" in round_city_stats:
                for round_city_event in round_city_stats["events"]:
                    if round_city_event["type"] == "outbreak":
                        city_pathogens[round_city_name].append(round_city_event["pathogen"])
                        city_pathogens_names[round_city_name].append(round_city_event["pathogen"]["name"])

        # count how many cities are affected by each pathogen
        for pathogens_encountered_name in pathogens_encountered_names:
            affected_cities = 0
            for round_city_name, _ in round_cities.items():
                if pathogens_encountered_name in city_pathogens_names[round_city_name]:
                    affected_cities += 1
            pathogens_count_infected_cities[pathogens_encountered_name] = affected_cities

        # debug output for generated lists
        if False:
            print(possible_operations_names)
            print(pathogens_medication_in_development_names)
            print(pathogens_medication_available_names)
            print(pathogens_encountered_names)
            print(city_pathogens_names)
            print(pathogens_count_infected_cities)

            print(sorted(ranking.items(), key=lambda item: item[1], reverse=True))

        # iterate over ranked operations to determine action
        for key, value in sorted(ranking.items(), key=lambda item: item[1], reverse=True):
            # print("took", key, "with", value, "points")
            op_name, *op_rest = key
            if operations.PRICES[op_name]["initial"] <= round_points:
                return operations.get(op_name, *op_rest)
            else:
                continue
        return operations.get("end_round")


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
    print("Wrong symbols")


def count_infected_cities(pathogen_name, city_pathogens):
    count = 0
    for city, pathogens in city_pathogens.items():
        if pathogen_name in pathogens:
            count += 1
    return count
