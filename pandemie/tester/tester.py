import math
import os
import subprocess
import datetime
import random
from pandemie.tester import AbstractStrategy
from pandemie.web import start_server

# consts used to shift the sigmoid curve
WIN_RATE_HALVED = 25
LOSS_RATE_HALVED = 25
EVALUATION_SLOPE = 0.1

DEVNULL = subprocess.DEVNULL


def to_camel_case(name):
    return name.title().replace("_", "")


class Tester:
    def __init__(self, test_strategy, random_seed=True):
        if not isinstance(test_strategy, AbstractStrategy):
            raise ValueError("Strategy is not valid.")

        if not test_strategy.silent:
            strategy_dir = "results/" + test_strategy.name

            # Create a directory for the strategy if it doesn't exists
            if not os.path.exists(strategy_dir):
                os.makedirs(strategy_dir)

            # Create the name for the log file and pass it to the strategy
            test_strategy.set_file("{0}-{1}.dat".format(test_strategy.name, self.now()))

        self.strategy = test_strategy

        self.random_seed = rand_seed

        self.seed = 0
        self.new_seed()

    def _run_strategy(self):
        print("================== NEW SEED: %s ==================" % str(self.seed))

        # store cwd for later usage
        cwd = os.getcwd()
        os.chdir("../../test")

        if os.name == "nt":
            subprocess.Popen("ic20_windows.exe --random-seed {0}".format(self.seed), stdout=DEVNULL,
                             stderr=DEVNULL)
        else:
            subprocess.Popen(["./ic20_linux", "--random-seed",  str(self.seed)], stdout=DEVNULL,
                             stderr=DEVNULL)

        # restore cwd
        os.chdir(cwd)

        # increment seed
        self.new_seed()

        # start server and wait for round to end
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
    def win_weight(rounds, k=EVALUATION_SLOPE):
        return math.exp(k*(-rounds + WIN_RATE_HALVED)) / (1 + math.exp(k*(-rounds + WIN_RATE_HALVED)))

    @staticmethod
    def loss_weight(rounds):
        return Tester.win_weight(rounds, k=-EVALUATION_SLOPE) - 1

    @staticmethod
    def now():
        return str(datetime.datetime.today().strftime('%Y-%m-%d--%H.%M.%S'))

    def new_seed(self):
        if self.random_seed:
            self.seed = random.randint(1, 10000000000)
        else:
            self.seed += 1


if __name__ == "__main__":
    strategy_name = input("Enter the full name of the strategy you want to test (no .py):\t")
    do_output = input("Should a log be created? (y/n, default=n)\t").lower()
    do_output = do_output.startswith("y") or do_output.startswith("j")
    visualize = input("Should the data be visualized? (y/n, default=n):\t")
    visualize = visualize.startswith("y") or visualize.startswith("j")

    while True:
        count = input("How many rounds should the simulation last? (default=5)\t")

        if not count:
            count = 5
            break

        elif not count.isdigit():
            print("You need to enter a valid round number!")

        else:
            count = int(count)
            break

    rand_seed = input("Do you want a random seed? (y/n, default=y)").lower()
    rand_seed = rand_seed.startswith("y") or rand_seed.startswith("j") or rand_seed == ""

    strategy = ""

    try:
        strategy_mod = __import__("pandemie.tester.strategies." + strategy_name, fromlist=to_camel_case(strategy_name))
        strategy = getattr(strategy_mod, to_camel_case(strategy_name))

    except ModuleNotFoundError:
        print("StrategyModule {0} not found! Exiting...".format(strategy_name))
        exit()

    except AttributeError:
        print("Strategy not found! Make sure it has the same name as the file. Exiting...")
        exit()

    my_tester = Tester(strategy(silent=not do_output, visualize=visualize), random_seed=rand_seed)
    result = my_tester.evaluate(times=count)
    print(result)
