from abc import ABC, abstractmethod
import string
from pandemie.event_checker import EventChecker


class AbstractStrategy(ABC):
    def __init__(self, name, silent=False):
        super().__init__()
        self.result = None
        self.name = name  # Name of the strategy
        self.file = ""
        self.silent = silent  # If False -> Output result and pathogens of each round into a file
        self.data_gatherer = EventChecker()

    def set_file(self, file):
        self.file = file

    def solve(self, json_data, server):

        # warning, we actually do not send a last response after the game finished
        # todo: check the unknown behaviour of the ic20 tool

        self.data_gatherer.check_all_events(json_data)  # Check for new Events and Pathogens

        if not json_data["outcome"] == "pending":  # Round ended
            self.result = (json_data["outcome"], json_data["round"])  # Set the result

            if not self.silent:  # If there should be an output
                with open("results/" + self.name + "/" + self.file, "a") as file:  # Open the save-file
                    data = json_data["outcome"] + ":\t" + str(json_data["round"]) + "\n"  # Outcome + played rounds
                    if "events" in json_data:  # Get all pathogens which occurred during the round
                        for event in json_data["events"]:
                            if event["type"] == "pathogenEncountered":
                                data += str(event["pathogen"]) + "\n"  # Add the data of the pathogen

                    data += "\n"
                    data = "".join(x for x in data if x in string.printable)  # Remove all non UTF-8 characters
                    file.write(data)

            server.shutdown()

        return self._solve(json_data, server)

    @abstractmethod
    def _solve(self, json_data, server):
        pass

    def get_result(self):
        return self.result
