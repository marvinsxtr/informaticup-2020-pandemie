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
    def __init__(self, strategy, random_seed=None):
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

        if not random_seed:
            self.random_seed = random.randint(0, 1000)
        else:
            self.random_seed = random_seed

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

        if not self.strategy.silent:
            with open(self.strategy.get_file_path(), "a") as file:
                file.write(str(weighted_sum / len(results)))

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
    strategy_name = input("Welche Strategie soll ausgeführt werden? (ohne.py)\t")
    do_output = input("Soll ein log-output erzeugt werden? (j/n)\t")

    do_output = not ("y" in do_output.lower() or "j" in do_output.lower())

    all_strategies = {
        "marvin1": Marvin1("marvin", silent=do_output),
        "example": ExampleStrategy("example", silent=do_output)
    }

    if strategy_name in all_strategies:
        my_tester = Tester(all_strategies[strategy_name], random_seed=0)
        result = my_tester.evaluate(times=1)
        print(result)
    else:
        print("Der Name konnte nicht gefunden werden!")
    #my_tester = Tester(ExampleStrategy("example"))
    #result = my_tester.evaluate(times=2)
    #print(result)
