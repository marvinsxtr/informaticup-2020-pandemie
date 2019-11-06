from pandemie.tester import AbstractStrategy
from pandemie import operations


class ExampleStrategy(AbstractStrategy):
    def __init__(self, silent=False):
        super().__init__(silent=silent)

    def _solve(self, json_data, server):
        return operations.end_round()

    def get_result(self):
        return self.result
