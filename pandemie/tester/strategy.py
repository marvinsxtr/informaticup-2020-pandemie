import os
from abc import ABC, abstractmethod

import json

from pandemie.event_checker import EventChecker
from pandemie.util.encoding import filter_unicode
import errno


class AbstractStrategy(ABC):
    def __init__(self, silent=False, visualize=False):
        super().__init__()
        self.result = None
        self.file = ""
        self.silent = silent  # If False -> Output result and pathogens of each round into a file
        self.visualize = visualize  # Writes json for every round into file to be visualized
        self.data_gatherer = EventChecker()

    def set_file(self, file):
        self.file = file

    @staticmethod
    def log_json(json_data):
        filename = "tmp/current_json.dat"
        if not os.path.exists(os.path.dirname(filename)):
            try:
                os.makedirs(os.path.dirname(filename))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        with open(filename, 'w+') as outfile:
            # todo: fix encoding
            outfile.write(json.dumps(json_data))
            outfile.flush()
            os.fsync(outfile.fileno())

    def solve(self, json_data, server):

        # update current data for visualization
        if self.visualize:
            self.log_json(json_data)

        # warning, we actually do not send a last response after the game finished
        # todo: check the unknown behaviour of the ic20 tool

        self.data_gatherer.check_all_events(json_data)  # Check for new Events and Pathogens

        if not json_data["outcome"] == "pending":  # Round ended
            self.result = (json_data["outcome"], json_data["round"])  # Set the result

            if not self.silent:

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

            # shutdown server
            server.stop()

        return self._solve(json_data, server)

    @abstractmethod
    def _solve(self, json_data, server):
        pass

    def get_result(self):
        return self.result

    def get_file_path(self):
        return "results/" + self.name + "/" + self.file

    @property
    def name(self):
        return self.__class__.__name__
