import math
import os
import random
import subprocess
import sys
import threading
import getopt
import pandemie.tester.optimization as optimization  # We cannot use import from due to circular imports

from pandemie.tester import AbstractStrategy
from pandemie.web import WebServer
from pandemie.util import to_camel_case, now

# Consts used to shift the sigmoid curve
WIN_RATE_HALVED = 75
LOSS_RATE_HALVED = 75
EVALUATION_SLOPE = 0.07

DEVNULL = subprocess.DEVNULL

MAX_THREADS = 500


class Tester:
    """
    The Tester. It evaluates a strategy by testing it multiple time with the ica test tool. Then it calculates an
    average score by converting each round into a float score.
    """
    def __init__(self, test_strategy, seed=0):
        if not isinstance(test_strategy, AbstractStrategy):
            raise ValueError("Strategy is not valid.")

        if not test_strategy.silent:
            strategy_dir = "logs/" + test_strategy.name

            # Create a directory for the strategy if it doesn't exists
            if not os.path.exists(strategy_dir):
                os.makedirs(strategy_dir)

            # Create the name for the log file and pass it to the strategy
            test_strategy.set_file("{0}-{1}.dat".format(test_strategy.name, now()))

        self.strategy = test_strategy
        self.seed = seed
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

        # Store cwd for later usage
        cwd = os.getcwd()
        os.chdir("../../test")

        # Starting all threads
        for i, thread in enumerate(threads):
            thread.start()
            sys.stdout.write("\r \rStarted %d / %d threads" % (i+1, thread_count))
            sys.stdout.flush()
        sys.stdout.write("\n")

        # Restore cwd
        os.chdir(cwd)

        # Waiting for threads and the server to be finished
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

            if r[0] == "win":
                self.amount_wins += 1
                w = self.win_weight(r[1])
            elif r[0] == "loss":
                self.amount_loss += 1
                w = self.loss_weight(r[1])
            else:
                raise ValueError("Unknown result type {0}".format(r[0]))

            weighted_sum += w
            print("Game {0}: {1} after {2} rounds and score: {3:4f}".format(i + 1, r[0], r[1], w))

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


def main():
    """
    Main program flow
    :return: None
    """
    strategy_name = "final"     # default strategy name
    do_output = False       # default log value
    visualize = False       # default value for visualization
    count = 5       # default value for amount of threads
    user_seed = 0       # default user seed, will be overwritten when user uses non random seed (0 = randomness)
    strategy_mod = __import__("pandemie.tester.strategies." + strategy_name, fromlist=to_camel_case(strategy_name))
    strategy = getattr(strategy_mod, to_camel_case(strategy_name))

    # read commandline arguments, first
    full_cmd_arguments = sys.argv

    # - further arguments
    argument_list = full_cmd_arguments[1:]

    # define allowed cli arguments
    unix_options = "hos:lvt:u"
    gnu_options = ["help", "optimize", "log", "visualization", "user_seed"]

    try:
        arguments, values = getopt.getopt(argument_list, unix_options, gnu_options)
    except getopt.error as err:
        # output error, and return with an error code
        print(str(err))
        sys.exit(2)

    # execute commands to chosen arguments
    for currentArgument, currentValue in arguments:
        if currentArgument in ("-h", "--help"):
            print("-h --help            show the help\n"
                  "-o --optimize        enable optimization for the final strategy\n"
                  "-s                   add the full name of the strategy you want to test (no .py) (default=final)\n"
                  "-l --log             write down log of run\n"
                  "-v --visualization   save visualization data for one thread\n"
                  "-t                   how many simulations should be run simultaneously? (default=5)\n"
                  "-u --user_seed       uses a predefined seed for all games, if not set a random seed is used\n")
            if len(arguments) < 2:
                exit()
        elif currentArgument in ("-o", "--optimize"):
            print("Optimizing final strategy")
            optimization.bayesian_optimization()
            exit()
        elif currentArgument in ("-s", ):
            strategy_name = currentValue
            try:
                strategy_mod = __import__("pandemie.tester.strategies." + strategy_name,
                                          fromlist=to_camel_case(strategy_name))
                strategy = getattr(strategy_mod, to_camel_case(strategy_name))

            except ModuleNotFoundError:
                print("StrategyModule {0} not found! Exiting...".format(strategy_name))
                exit()

            except AttributeError:
                print("Strategy not found! Make sure it has the same name as the file. Exiting...")
                exit()
        elif currentArgument in ("-l", "--log"):
            do_output = True
        elif currentArgument in ("-v", "--visualization"):
            visualize = True
        elif currentArgument in ("-t", ):
            if not currentValue.isdigit():
                print("You need to enter a valid thread number!")
                exit()
            count = int(currentValue)
            if count > MAX_THREADS:
                count = MAX_THREADS
                print("The amount of threads is limited to {0}. The number of threads got reduced".format(
                    MAX_THREADS))
        elif currentArgument in ("-u", "--user_seed"):
            user_seed = currentValue
            if not user_seed.isdigit():
                print("You need to enter a valid user seed!")
                exit()
            user_seed = int(user_seed)

    if visualize:
        print("Reduced thread number to 1 since we want to store the data for the visualization.")
        count = 1

    my_tester = Tester(strategy(silent=not do_output, visualize=visualize), seed=user_seed)

    # Execute tester
    result = my_tester.evaluate(thread_count=count)

    # Print stats
    percentage = (my_tester.amount_wins / my_tester.amount_runs) * 100
    print("\nTotal games: {0}\nTotal games won: {1}\nTotal games loss: {2}\nWin rate: {3}%".format(
        my_tester.amount_runs,
        my_tester.amount_wins,
        my_tester.amount_loss,
        percentage))

    print("Total score: ", result)


# Execute here if we run this python file
if __name__ == "__main__":
    main()
