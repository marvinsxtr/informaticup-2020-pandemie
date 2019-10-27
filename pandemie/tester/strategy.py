from abc import ABC, abstractmethod


class AbstractStrategy(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def solve(self, json_data, server):
        pass

    @abstractmethod
    def get_result(self):
        pass
