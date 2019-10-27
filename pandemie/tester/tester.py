import os
import subprocess
from pandemie.tester import AbstractStrategy
from pandemie.web import start_server
from pandemie import operations


class Tester:
    def __init__(self, strategy, random_seed=0):
        if not isinstance(strategy, AbstractStrategy):
            raise ValueError("Strategy is not valid.")
        self.strategy = strategy
        self.random_seed = random_seed

    def run_strategy(self):
        if os.name == "nt":
            os.system(
                "start ../../test/ic20_windows.exe --random-seed {0}".format(self.random_seed))

        else:
            os.chdir("../../test/")
            subprocess.call(
                "./ic20_linux --random-seed {0}".format(self.random_seed), shell=True)

        start_server(self.strategy)

        return self.strategy.get_result()


class ExampleStrategy(AbstractStrategy):
    def __init__(self):
        super().__init__()

    def _solve(self, json_data, server):
        return operations.end_round()

    def get_result(self):
        return self.result


if __name__ == "__main__":
    my_tester = Tester(ExampleStrategy())
    result = my_tester.run_strategy()
    print(result)
