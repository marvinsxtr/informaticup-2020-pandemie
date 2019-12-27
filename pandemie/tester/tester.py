import datetime
import math
import os
import random
import subprocess
import sys
import time
import threading
from pandemie.tester import AbstractStrategy
from pandemie.web import WebServer

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
        self.seed = 0
        self.random_seed = random_seed
        self.amount_wins = 0
        self.amount_loss = 0
        self.amount_runs = 0


    def _start_tester(self):
        if os.name == "nt":
            subprocess.call("ic20_windows.exe --random-seed {0}".format(self.seed), stdout=DEVNULL, stderr=DEVNULL,
                            shell=True)
        else:
            subprocess.call(["./ic20_linux", "--random-seed " + str(self.seed)], stdout=DEVNULL, stderr=DEVNULL,
                            shell=True)

    def _thread_seed(self):
        if self.random_seed:
            self.seed = self.new_seed()
        else:
            self.seed = self.seed + 1

    def evaluate(self, thread_count=10):
        self.amount_runs = thread_count

        threads = [threading.Thread(target=self._start_tester,) for _ in range(thread_count)]
        server = WebServer(self.strategy)
        server.start()

        # store cwd for later usage
        cwd = os.getcwd()
        os.chdir("../../test")

        # starting all threads
        for i, t in enumerate(threads):
            self._thread_seed()
            t.start()
            sys.stdout.write("\r \rStarted %d / %d threads" % (i+1, thread_count))
            sys.stdout.flush()
        sys.stdout.write("\n")

        # restore cwd
        os.chdir(cwd)

        # waiting for threads and the server to be finished
        for i, t in enumerate(threads):
            sys.stdout.write("\r \rWaiting for threads to finish: %d / %d" % (i, thread_count))
            sys.stdout.flush()
            t.join()
        sys.stdout.write("\n")

        results = self.strategy.get_result()

        print("Stopping server...")
        server.stop()

        weighted_sum = 0
        i = 1
        for r in results:
            if r[0] == "win":
                weighted_sum += self.win_weight(r[1])
                print("Game ", i, " :", r[0], " after ", r[1], " rounds and score: ", self.win_weight(r[1]))
                i += 1
                self.amount_wins += 1
            elif r[0] == "loss":
                weighted_sum += self.loss_weight(r[1])
                print("Game ", i, " :", r[0], " after ", r[1], " rounds and score: -", self.win_weight(r[1]))
                i += 1
                self.amount_loss += 1
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

    @staticmethod
    def new_seed():
        return random.randint(1, 100000000000)


if __name__ == "__main__":
    strategy_name = input("Enter the full name of the strategy you want to test (no .py) (default=final):\t")

    # set default strategy
    if not strategy_name:
        strategy_name = "final"

    # checking stratagie file is avaliable
    try:
        f = open("strategies/"+strategy_name+".py")

    except IOError:
        print("Stratagie name not valid")
        exit()

    do_output = input("Should a log be created? (y/n, default=n):\t").lower()
    do_output = do_output.startswith("y") or do_output.startswith("j")
    visualize = input("Do you want the data of one round to be saved for visualization? (y/n, default=n):\t")
    visualize = visualize.startswith("y") or visualize.startswith("j")

    if not visualize:
        while True:
            count = input("How many simulations should be run simultaneously? (default=5):\t")

            if not count:
                count = 5
                break

            elif not count.isdigit():
                print("You need to enter a valid round number!")

            else:
                count = int(count)
                # prevent to much threads on machine
                if count > 500:
                    count = 500
                    print("The amount of threads is limited to 500. The amount of threads was set to 500.")
                break
    else:
        count = 1

    rand_seed = input("Do you want a random seed? (y/n, default=y):\t").lower()
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
    result = my_tester.evaluate(thread_count=count)
    print(" Total games:", my_tester.amount_runs, "\n",
          "Total games won:", my_tester.amount_wins, "\n",
          "Total games loss:", my_tester.amount_loss, "\n",
          "Win rate:", str((my_tester.amount_wins / my_tester.amount_runs) * 100),
          "%")
    print(" Total score: ", result)
