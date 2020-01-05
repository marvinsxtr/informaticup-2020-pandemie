import threading

from abc import ABC, abstractmethod

from pandemie.event_checker import EventChecker
from pandemie.util import filter_unicode, log_json


class AbstractStrategy(ABC):
    """
    An abstract template for strategies with all necessary functionalities, default run values and integrated
    data-gatherer
    """
    def __init__(self, silent=True, visualize=False, weights=None):
        """
        :param silent: default:True; Determines whether log is created or not
        :param visualize: default:False; Determines whether data is saved for visualisation or not
        :param weights: Weights for weighted decision
        """
        super().__init__()
        self.weights = weights
        self.result = []
        self.file = ""
        self.silent = silent  # If False -> Output result and pathogens of each round into a file
        self.visualize = visualize  # Writes json for every round into file to be visualized
        self.data_gatherer = EventChecker()
        self.lock = threading.Lock()

    def set_file(self, file):
        """
        Function to set the name of the logfile
        :param file: name of the logfile
        """
        self.file = file

    def log_result(self, json_data):
        """
        Function to write the round-data into a logfile
        :param json_data: raw data for the current round
        """
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

    def solve(self, json_data):
        """
        Function to decide the operation used in the current round and do log + data-gathering
        :param json_data: raw data for the current round
        :return: operation applied for this round
        """

        # Update current data for visualization
        if self.visualize:
            log_json(json_data)

        # Warning, we actually do not send a last response after the game finished
        # Todo: check the unknown behaviour of the ic20 tool
        self.data_gatherer.parse_data(json_data)  # Check for new Events and Pathogens

        if not json_data["outcome"] == "pending":  # Round ended

            self.lock.acquire()
            self.result.append((json_data["outcome"], json_data["round"]))
            self.lock.release()

            if not self.silent:
                self.log_result(json_data)  # Log cumulative results

        return self._solve(json_data)

    @abstractmethod
    def _solve(self, json_data):
        """
        Function gets implemented to decide the operation used
        :param json_data: raw data of the current round
        :return: operation to apply
        """
        pass

    def get_result(self):
        """
        Getter-function for all outcomes of the played games
        :return: List containing outcome - survived Rounds tuples
        """
        return self.result

    def get_file_path(self):
        """
        Helper-function to return the dynamic path to the logfile
        :return: path to the logfile
        """
        return "results/" + self.name + "/" + self.file

    @property
    def name(self):
        """
        The name of the strategy for easier usage
        :return: Classname
        """
        return self.__class__.__name__
