import errno
import os
import json
import threading

from abc import ABC, abstractmethod

from pandemie.event_checker import EventChecker
from pandemie.util.encoding import filter_unicode


class AbstractStrategy(ABC):
    def __init__(self, silent=False, visualize=False, weights=None):
        super().__init__()
        self.weights = weights
        self.result = []
        self.file = ""
        self.silent = silent  # If False -> Output result and pathogens of each round into a file
        self.visualize = visualize  # Writes json for every round into file to be visualized
        self.data_gatherer = EventChecker()
        self.lock = threading.Lock()

    def set_file(self, file):
        self.file = file

    def log_result(self, json_data):
        # Save strategy data
        with open(self.get_file_path(), "a") as file:

            # Dump outcome and played rounds
            data = "{0}:\t{1}\n".format(json_data["outcome"], str(json_data["round"]))

            # Append all pathogens which occurred during the round
            if "events" in json_data:
                for event in json_data["events"]:
                    if event["type"] == "pathogenEncountered":
                        data += str(event["pathogen"]) + "\n"  # Add the data of the pathogen

            data += "\n"
            data = filter_unicode(data)  # Remove all non UTF-8 characters
            file.write(data)

    @staticmethod
    def log_json(json_data):
        # delete files for new game
        if json_data["round"] == 1:
            path = os.getcwd()
            rounds = os.listdir(path + "/tmp/")

            for round_name in rounds:
                os.remove(path + "/tmp/" + round_name)

        # creates a file if it does not exist yet
        def create_file(filename):
            if not os.path.exists(os.path.dirname(filename)):
                try:
                    os.makedirs(os.path.dirname(filename))
                except OSError as exc:  # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise

        name = "tmp/round{0}.dat".format(json_data["round"])
        create_file(name)

        # update current_round.dat
        with open(name, 'w') as outfile:
            outfile.write(json.dumps(json_data))
            outfile.flush()
            os.fsync(outfile.fileno())

    def solve(self, json_data, server):

        # update current data for visualization
        if self.visualize:
            self.log_json(json_data)

        # warning, we actually do not send a last response after the game finished
        # todo: check the unknown behaviour of the ic20 tool
        self.data_gatherer.parse_data(json_data)  # Check for new Events and Pathogens

        if not json_data["outcome"] == "pending":  # Round ended

            self.lock.acquire()
            self.result.append((json_data["outcome"], json_data["round"]))
            self.lock.release()

            if not self.silent:
                self.log_result(json_data)  # log cumulative results

        return self._solve(json_data, server, self.weights)

    @abstractmethod
    def _solve(self, json_data, server, weights):
        pass

    def get_result(self):
        return self.result

    def get_file_path(self):
        return "results/" + self.name + "/" + self.file

    @property
    def name(self):
        return self.__class__.__name__
