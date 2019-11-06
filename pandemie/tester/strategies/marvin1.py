from pandemie.tester import AbstractStrategy
from pandemie import operations


class Marvin1(AbstractStrategy):
    def __init__(self, silent=False):
        super().__init__(silent=silent)

    def _solve(self, json_data, server):
        if "error" in json_data:
            print(json_data["error"])

        points = json_data["points"]
        round = json_data["round"]
        cities = json_data["cities"]

        print("solving with marvin1 in round", round)

        if points < 3:
            return operations.end_round()

        for key, value in sorted(cities.items(), key=lambda item: get_single_score(item[1]["hygiene"])):
            if get_single_score(value["hygiene"]) == 1:
                return operations.apply_hygienic_measures(key)

        for key, value in sorted(cities.items(), key=lambda item: get_single_score(item[1]["awareness"])):
            if get_single_score(value["awareness"]) == 1:
                return operations.launch_campaign(key)

        for key, value in sorted(cities.items(), key=lambda item: get_single_score(item[1]["government"])):
            if get_single_score(value["government"]) == 1:
                return operations.call_elections(key)

        for key, value in sorted(cities.items(), key=lambda item: get_single_score(item[1]["economy"])):
            if get_single_score(value["economy"]) == 1:
                return operations.exert_influence(key)

        return operations.end_round()


def get_single_score(symbols):
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
    print("wrong symbols")
