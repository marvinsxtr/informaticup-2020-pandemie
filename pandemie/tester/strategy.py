from abc import ABC, abstractmethod


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
            server.shutdown()

        return self._solve(json_data, server)

    @abstractmethod
    def _solve(self, json_data, server):
        pass

    @abstractmethod
    def get_result(self):
        pass
