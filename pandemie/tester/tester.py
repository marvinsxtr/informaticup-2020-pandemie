import datetime
import math
import os
import random
import subprocess
import sys
import threading
from pandemie.tester import AbstractStrategy
from pandemie.web import WebServer
from bayes_opt import BayesianOptimization, JSONLogger
from bayes_opt.event import Events

# consts used to shift the sigmoid curve
WIN_RATE_HALVED = 25
LOSS_RATE_HALVED = 25
EVALUATION_SLOPE = 0.1

DEVNULL = subprocess.DEVNULL
TIME_FORMAT = "%Y-%m-%d--%H.%M.%S"

MAX_THREADS = 500


def to_camel_case(name):
    """
    Converts a name into its camel case equivalent.
    Example `to_camel_case` -> `ToCamelCase`
    :param name: string to be converted
    :return: camel case name
    """
    return name.title().replace("_", "")


def now():
    """
    Returns the current time.
    :return: current time
    """
    return datetime.datetime.today().strftime(TIME_FORMAT)


def block_print():
    sys.stdout = open(os.devnull, 'w')


def enable_print():
    sys.stdout = sys.__stdout__


def weighted_final_strategy(put_under_quarantine_weight, develop_medication_weight, deploy_medication_weight):
    weights = (put_under_quarantine_weight, develop_medication_weight, deploy_medication_weight)

    name = "final"
    module = __import__("pandemie.tester.strategies." + name, fromlist=to_camel_case(name))
    final_strategy = getattr(module, to_camel_case(name))

    block_print()
    tester = Tester(final_strategy(silent=True, visualize=False, weights=weights), random_seed=False)
    score = tester.evaluate(thread_count=50)
    enable_print()

    win_rate = (tester.amount_wins / tester.amount_runs)
    return score + win_rate


def bayesian_optimization():
    # Bounded region of parameter space
    pbounds = {'put_under_quarantine_weight': (0.2, 1.8),
               'develop_medication_weight': (0.2, 1.8),
               'deploy_medication_weight': (0.2, 1.8)}

    optimizer = BayesianOptimization(
        f=weighted_final_strategy,
        pbounds=pbounds,
        random_state=1,
    )

    logger = JSONLogger(path="./logs/bayes_logs.json")
    optimizer.subscribe(Events.OPTMIZATION_STEP, logger)

    optimizer.maximize(
        init_points=5,
        n_iter=50,
    )


class Tester:
    """
    The Tester. It evaluates a strategy by testing it multiple time with the ica test tool. Then it calculates an
    average score by converting each round into a float score.
    """
    def __init__(self, test_strategy, random_seed=True):
        if not isinstance(test_strategy, AbstractStrategy):
            raise ValueError("Strategy is not valid.")

        if not test_strategy.silent:
            strategy_dir = "results/" + test_strategy.name

            # Create a directory for the strategy if it doesn't exists
            if not os.path.exists(strategy_dir):
                os.makedirs(strategy_dir)

            # Create the name for the log file and pass it to the strategy
            test_strategy.set_file("{0}-{1}.dat".format(test_strategy.name, now()))

        self.strategy = test_strategy
        self.seed = 1
        self.random_seed = random_seed
        self.amount_wins = 0
        self.amount_loss = 0
        self.amount_runs = 0

    def _start_tester(self):
        """
        Starts the ica test tool as a subprocess.
        :return: None
        """
        if os.name == "nt":
            subprocess.call("ic20_windows.exe --random-seed {0}".format(self.seed), stdout=DEVNULL, stderr=DEVNULL,
                            shell=True)
        else:
            subprocess.call(["./ic20_linux", "--random-seed " + str(self.seed)], stdout=DEVNULL, stderr=DEVNULL,
                            shell=True)

    def _thread_seed(self):
        """
        Sets the next seed either as a random one or increments the old one by 1.
        :return: None
        """
        if self.random_seed:
            self.seed = self.new_seed()
        else:
            self.seed = self.seed + 1

    def evaluate(self, thread_count=10):
        """
        Evaluates the current strategy. For each game a new thread is started.
        :param thread_count: number of threads to be started
        :return: the average score
        """
        self.amount_runs = thread_count

        threads = [threading.Thread(target=self._start_tester,) for _ in range(thread_count)]
        server = WebServer(self.strategy)
        server.start()

        # store cwd for later usage
        cwd = os.getcwd()
        os.chdir("../../test")

        # starting all threads
        for i, thread in enumerate(threads):
            self._thread_seed()
            thread.start()
            sys.stdout.write("\r \rStarted %d / %d threads" % (i+1, thread_count))
            sys.stdout.flush()
        sys.stdout.write("\n")

        # restore cwd
        os.chdir(cwd)

        # waiting for threads and the server to be finished
        for i, thread in enumerate(threads):
            sys.stdout.write("\r \rWaiting for threads to finish: %d / %d" % (i, thread_count))
            sys.stdout.flush()
            thread.join()
        sys.stdout.write("\n")

        results = self.strategy.get_result()

        print("Stopping server...")
        server.stop()

        weighted_sum = 0
        for i, r in enumerate(results):
            print("Game {0}: {1} after {2} rounds and score: {3:4f}".format(i + 1, r[0], r[1], self.win_weight(r[1])))
            weighted_sum += self.win_weight(r[1])

            if r[0] == "win":
                self.amount_wins += 1
            elif r[0] == "loss":
                self.amount_loss += 1
            else:
                raise ValueError("Unknown result type {0}".format(r[0]))

        if not self.strategy.silent:
            with open(self.strategy.get_file_path(), "a") as file:
                file.write(str(weighted_sum / len(results)))

        return weighted_sum / len(results)

    @staticmethod
    def win_weight(rounds, k=EVALUATION_SLOPE):
        """
        Calculates the win score using a sigmoid curve.
        :param rounds: amount of rounds
        :param k: parameter alter the slope of the sigmoid curve
        :return: score
        """
        return math.exp(k*(-rounds + WIN_RATE_HALVED)) / (1 + math.exp(k*(-rounds + WIN_RATE_HALVED)))

    @staticmethod
    def loss_weight(rounds):
        """
        Calculates the loss score using a sigmoid curve. This is the win weight with an inverse slope minus one.
        :param rounds: amount of rounds
        :return: score
        """
        return Tester.win_weight(rounds, k=-EVALUATION_SLOPE) - 1

    @staticmethod
    def new_seed():
        """
        Generates a new random seed.
        :return: random integer between 1 and 100000000000
        """
        return random.randint(1, 100000000000)


if __name__ == "__main__":
    optimize_strategy = input("Do you want to optimize the final strategy? (y/n, default=n):\t").lower()
    optimize_strategy = optimize_strategy.startswith("y") or optimize_strategy.startswith("j")

    if optimize_strategy:
        bayesian_optimization()
        exit()

    strategy_name = input("Enter the full name of the strategy you want to test (no .py) (default=final):\t")

    # set default strategy
    if not strategy_name:
        strategy_name = "final"

    strategy = None

    try:
        strategy_mod = __import__("pandemie.tester.strategies." + strategy_name, fromlist=to_camel_case(strategy_name))
        strategy = getattr(strategy_mod, to_camel_case(strategy_name))

    except ModuleNotFoundError:
        print("StrategyModule {0} not found! Exiting...".format(strategy_name))
        exit()

    except AttributeError:
        print("Strategy not found! Make sure it has the same name as the file. Exiting...")
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
                if count > MAX_THREADS:
                    count = MAX_THREADS
                    print("The amount of threads is limited to {0}. The number of threads got reduced".format(
                        MAX_THREADS))
                break
    else:
        count = 1

    rand_seed = input("Do you want a random seed? (y/n, default=y):\t").lower()
    rand_seed = rand_seed.startswith("y") or rand_seed.startswith("j") or rand_seed == ""

    my_tester = Tester(strategy(silent=not do_output, visualize=visualize), random_seed=rand_seed)

    # execute tester
    result = my_tester.evaluate(thread_count=count)

    # print stats
    percentage = (my_tester.amount_wins / my_tester.amount_runs) * 100
    print("\nTotal games: {0}\nTotal games won: {1}\nTotal games loss: {2}\nWin rate: {3}%".format(
        my_tester.amount_runs,
        my_tester.amount_wins,
        my_tester.amount_loss,
        percentage))

    print("Total score: ", result)
