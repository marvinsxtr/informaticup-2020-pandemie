from pandemie.tester import AbstractStrategy
from pandemie import operations
import random


class Ruwen2(AbstractStrategy):
    def __init__(self, silent=False):
        super().__init__(silent=silent)

    def _solve(self, data, server):
        return operations.end_round()
