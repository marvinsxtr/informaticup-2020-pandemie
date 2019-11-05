from pandemie.tester import AbstractStrategy
from pandemie import operations


class Marvin1(AbstractStrategy):
    def __init__(self, name):
        super().__init__(name)

    def _solve(self, json_data, server):
        if "error" in json_data:
            print(json_data["error"])

        points = json_data["points"]
        round = json_data["round"]

        cities = dict()

        for city in json_data["cities"]:
            cities[city] = 0
        print(cities)
        return operations.end_round()

    def get_result(self):
        return self.result


def get_single_score(symbols):
    if symbols == "--":
        return 0
    if symbols == "-":
        return 1
    if symbols == "o":
        return 2
    if symbols == "+":
        return 3
    if symbols == "++":
        return 4
    print("wrong symbols")
