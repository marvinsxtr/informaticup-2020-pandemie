from pandemie.tester import AbstractStrategy
from pandemie import operations
import random


class Ruwen2(AbstractStrategy):
    def __init__(self, silent=False, visualize=False):
        super().__init__(silent=silent, visualize=visualize)

    def _solve(self, data):
        return operations.end_round()
