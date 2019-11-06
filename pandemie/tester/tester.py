import math
import os
import subprocess
import datetime
import random
from pandemie.tester import AbstractStrategy
from pandemie.tester.strategies.marvin1 import Marvin1
from pandemie.web import start_server
from pandemie import operations

# consts used to shift the sigmoid curve
WIN_RATE_HALVED = 25
LOSS_RATE_HALVED = 25


class Tester:
    def __init__(self, strategy, random_seed=0):
        if not isinstance(strategy, AbstractStrategy):
            raise ValueError("Strategy is not valid.")

        if not strategy.silent:
            strategy_dir = "results/" + strategy.name

            # Create a directory for the strategy if it doesn't exists
            if not os.path.exists(strategy_dir):
                os.mkdir(strategy_dir)

            # Create the name for the log file and pass it to the strategy
            strategy.set_file("{0}-{1}.dat".format(strategy.name, self.now()))

        self.strategy = strategy
        self.random_seed = random.randint(0, 1000)

    def _run_strategy(self):
        if os.name == "nt":
            subprocess.call("start ../../test/ic20_windows.exe --random-seed {0}".format(self.random_seed), shell=True)

        else:
            os.chdir("../../test")
            subprocess.call("./ic20_linux --random-seed {0}".format(self.random_seed), shell=True)

        start_server(self.strategy)

        return self.strategy.get_result()

    def evaluate(self, times=10):
        results = [self._run_strategy() for _ in range(times)]
        weighted_sum = 0

        for r in results:
            if r[0] == "win":
                weighted_sum += self.win_weight(r[1])
            elif r[0] == "loss":
                weighted_sum += self.loss_weight(r[1])
            else:
                raise ValueError("Unknown result type {0}".format(r[0]))

        if not self.strategy.silent:  # If there should be an output
            with open("results/" + self.strategy.name + "/" + self.strategy.file, "a") as file:  # Open the save-file
                file.write(str(weighted_sum / len(results)))  # Append the score to the file

        return weighted_sum / len(results)

    @staticmethod
    def win_weight(rounds):
        return math.exp(-rounds + WIN_RATE_HALVED) / (1 + math.exp(-rounds + WIN_RATE_HALVED))

    @staticmethod
    def loss_weight(rounds):
        return math.exp(rounds - WIN_RATE_HALVED) / (1 + math.exp(rounds - WIN_RATE_HALVED)) - 1

    @staticmethod
    def now():
        return str(datetime.datetime.today().strftime('%Y-%m-%d--%H.%M.%S'))


class ExampleStrategy(AbstractStrategy):
    def __init__(self, name, silent=False):
        super().__init__(name, silent=silent)

    def _solve(self, json_data, server):
        return operations.end_round()

    def get_result(self):
        return self.result


if __name__ == "__main__":
    my_tester = Tester(Marvin1("marvin1", silent=False))
    result = my_tester.evaluate(times=1)
    print(result)

    #my_tester = Tester(ExampleStrategy("example"))
    #result = my_tester.evaluate(times=2)
    #print(result)
