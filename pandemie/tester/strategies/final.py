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
        round_events = json_data["events"]
        round_points = json_data["points"]
        round_number = json_data["round"]
        round_outcome = json_data["outcome"]

        # assigns each tuple of an operation a score
        ranking = {}

        put_under_quarantine_weight = 1
        close_airport_weight = 1
        close_connection_weight = 1

        develop_vaccine_weight = 1
        deploy_vaccine_weight = 1
        develop_medication_weight = 1
        deploy_medication_weight = 1

        exert_influence_weight = 1
        call_elections_weight = 1
        apply_hygienic_measures_weight = 1
        launch_campaign_weight = 1

        def rank_operation(*op_tuple, op_score):
            """
            rank an operation tuple with a score
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

        # pre-processing


        # print(sorted(ranking.items(), key=lambda item: item[1], reverse=True))
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
