from pandemie.tester import AbstractStrategy
from pandemie import operations


class Marvin2(AbstractStrategy):
    def __init__(self, silent=False, visualize=False):
        super().__init__(silent=silent, visualize=visualize)

    def _solve(self, json_data, server):
        if "error" in json_data:
            print(json_data["error"])
            return operations.end_round()

        cities = json_data["cities"]
        events = json_data["events"]
        points = json_data["points"]
        round = json_data["round"]
        outcome = json_data["outcome"]

        print(operations.PRICES["end_round"]["initial"])

        return operations.end_round()


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
    print("wrong symbols")


def count_infected_cities(pathogen_name, city_pathogens):
    count = 0
    for city, pathogens in city_pathogens.items():
        if pathogen_name in pathogens:
            count += 1
    return count
