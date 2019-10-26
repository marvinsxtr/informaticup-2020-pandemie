import os
import subprocess
from pandemie.tester import AbstractStrategy
from pandemie.web import start_server


class Tester:
    def __init__(self, strategy, random_seed=0):
        if not isinstance(strategy, AbstractStrategy):
            raise ValueError("Strategy is not valid.")

        if os.name == "nt":
            os.system("start ../../test/ic20_windows.exe --random-seed {0}".format(random_seed))

        else:
            os.chdir("../../test/")
            subprocess.call("./ic20_linux --random-seed {0}".format(random_seed), shell=True)

        start_server(strategy)


class ExampleStrategy(AbstractStrategy):
    def __init__(self):
        super().__init__()

    def solve(self, json_data):
        return '{"type": "endRound"}'


if __name__ == "__main__":
    my_tester = Tester(ExampleStrategy())
