from pandemie.tester import AbstractStrategy


class Tester(AbstractStrategy):
    def __init__(self):
        super().__init__()

    def solve(self, json_data):
        print("DO something")
