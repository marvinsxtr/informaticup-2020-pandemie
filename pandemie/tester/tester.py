import datetime
import math
import os
import random
import subprocess
import time
from multiprocessing import Process
import threading
from pandemie.tester import AbstractStrategy
from pandemie.web import start_server

# consts used to shift the sigmoid curve
WIN_RATE_HALVED = 25
LOSS_RATE_HALVED = 25
EVALUATION_SLOPE = 0.1
results = []
used_seeds = []
dir = 0

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

    def _start_tester(self):
        global dir
        if dir == 0:
            os.chdir("../../test")
            dir = 1

        if os.name == "nt":
            subprocess.call("ic20_windows.exe --random-seed {0}".format(self.seed), stdout=DEVNULL, stderr=DEVNULL,
                            shell=True)
        else:
            subprocess.call(["./ic20_linux", "--random-seed " + str(self.seed)], stdout=DEVNULL, stderr=DEVNULL,
                            shell=True)

    def _run_strategy(self):
        print("================== NEW SEED: %s ==================" % str(self.seed))

        # store cwd for later usage
        global used_seeds
        used_seeds.append(self.seed)
        cwd = os.getcwd()
        self._start_tester()
        # restore cwd
        os.chdir(cwd)

        # start server and wait for round to end
        # start_server(self.strategy)
        global results
        result = self.strategy.get_result()
        results.append(result)
        # print("Seeds in list", used_seeds, "got the result", result)

    def evaluate(self, times=10):
        # Thread based call of amount(times) instances of .self_run_strategy

        cwd = os.getcwd()
        threads = [threading.Thread(target=self._run_strategy,) for i in range(times)]
        server = threading.Thread(target=start_server, args=(self.strategy,))
        server.start()

        for t in threads:
            # time.sleep(0.1)
            t.start()
            # increment seed
            self.new_seed()

            print("Started thread with id: ", t.ident)

        # waiting for threads and the server to be finished
        for t in threads:
            t.join()
        server.join()

        global results

        weighted_sum = 0
        i = 1
        for r in results:
            if r[0] == "win":
                weighted_sum += self.win_weight(r[1])
                print("Game ", i, " :", r[0], " after ", r[1], " rounds and score: ", self.win_weight(r[1]))
                i += 1
            elif r[0] == "loss":
                weighted_sum += self.loss_weight(r[1])
                print("Game ", i, " :", r[0], " after ", r[1], " rounds and score: -", self.win_weight(r[1]))
                i += 1
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
    visualize = input("Do you want the data of one round to be saved for visualization? (y/n, default=n):\t")
    visualize = visualize.startswith("y") or visualize.startswith("j")

    if not visualize:
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
    else:
        count = 1

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
    print("Total score: ", result)
