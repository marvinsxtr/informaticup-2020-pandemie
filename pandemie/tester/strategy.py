from abc import ABC, abstractmethod


class AbstractStrategy(ABC):
    def __init__(self):
        super().__init__()
        self.result = None

    def solve(self, json_data, server):

        # warning, we actually do not send a last response after the game finished
        # todo: check the unknown behaviour of the ic20 tool

        if json_data["outcome"] == "loss":
            self.result = ("loss", json_data["round"])
            server.shutdown()

        elif json_data["outcome"] == "win":
            self.result = ("win", json_data["round"])
            server.shutdown()

        return self._solve(json_data, server)

    @abstractmethod
    def _solve(self, json_data, server):
        pass

    @abstractmethod
    def get_result(self):
        pass
