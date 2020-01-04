from pandemie.tester import AbstractStrategy
from pandemie.util import operations


class ExampleStrategy(AbstractStrategy):
    def __init__(self, silent=False, visualize=False):
        super().__init__(silent=silent, visualize=visualize)

    def _solve(self, json_data):
        return operations.end_round()

    def get_result(self):
        return self.result
