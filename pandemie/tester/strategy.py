from abc import ABC, abstractmethod
import string


class AbstractStrategy(ABC):
    def __init__(self, name):
        super().__init__()
        self.result = None
        self.name = name

    def solve(self, json_data, server):

        # warning, we actually do not send a last response after the game finished
        # todo: check the unknown behaviour of the ic20 tool

        if not json_data["outcome"] == "pending":
            self.result = (json_data["outcome"], json_data["round"])
            with open("results/" + self.name + ".dat", "a") as file:
                data = json_data["outcome"] + ":\t" + str(json_data["round"]) + "\n"
                if "events" in json_data:
                    for event in json_data["events"]:
                        if event["type"] == "pathogenEncountered":
                            data += str(event["pathogen"]) + "\n"

                data += "\n"
                data = "".join(x for x in data if x in string.printable)
                file.write(data)
            server.shutdown()

        return self._solve(json_data, server)

    @abstractmethod
    def _solve(self, json_data, server):
        pass

    @abstractmethod
    def get_result(self):
        pass
