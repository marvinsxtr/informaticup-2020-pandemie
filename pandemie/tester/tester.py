import math
import os
import subprocess
from pandemie.tester import AbstractStrategy
from pandemie.web import start_server
from pandemie import operations

# consts used to shift the sigmoid curve
WIN_RATE_HALVED = 25
LOSS_RATE_HALVED = 25


class Tester:
    def __init__(self, strategy, random_seed=0):
        if not isinstance(strategy, AbstractStrategy):
            raise ValueError("Strategy is not valid.")
        self.strategy = strategy
        self.random_seed = random_seed

    def _run_strategy(self):
        if os.name == "nt":
            os.system(
                "start ../../test/ic20_windows.exe --random-seed {0}".format(self.random_seed))

        else:
            os.chdir("../../test/")
            subprocess.call(
                "./ic20_linux --random-seed {0}".format(self.random_seed), shell=True)

        start_server(self.strategy)

        return self.strategy.get_result()

    def evaluate(self, times=1):
        results = [self._run_strategy() for _ in range(times)]
        weighted_sum = 0

        # todo: add a evaluation loop that somehow calculates a weighted average

    @staticmethod
    def win_weight(rounds):
        return math.exp(-rounds + WIN_RATE_HALVED) / (1 + math.exp(-rounds + WIN_RATE_HALVED))

    @staticmethod
    def loss_weight(rounds):
        return math.exp(rounds - WIN_RATE_HALVED) / (1 + math.exp(rounds - WIN_RATE_HALVED)) - 1


class ExampleStrategy(AbstractStrategy):
    def __init__(self):
        super().__init__()

    def _solve(self, json_data, server):
        return operations.end_round()

    def get_result(self):
        return self.result


if __name__ == "__main__":
    my_tester = Tester(ExampleStrategy())
    result = my_tester._run_strategy()
    print(result)
