from abc import ABC, abstractmethod


class AbstractStrategy(ABC):
    def __init__(self):
        super(AbstractStrategy, self).__init__()

    @abstractmethod
    def example(self):
        pass
