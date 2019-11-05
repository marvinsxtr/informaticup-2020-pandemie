from pandemie.tester import AbstractStrategy
from pandemie import operations


class Marvin1(AbstractStrategy):
    def __init__(self, name):
        super().__init__(name)

    def _solve(self, json_data, server):
        if "error" in json_data:
            print(json_data["error"])

        cities = dict()

        for city in json_data["cities"]:
            cities[city] = 0
        print(cities)
        return operations.end_round()

    def get_result(self):
        return self.result
