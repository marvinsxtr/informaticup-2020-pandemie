from pandemie.tester import AbstractStrategy
from pandemie.util import operations


class ExampleStrategy(AbstractStrategy):
    """
    This class is an example implementation of strategy.py
    This strategy is just for demonstration purposes on how to create your own strategy, it's only function is to end
    the current round.
    """
    def __init__(self, silent=False, visualize=False):
        super().__init__(silent=silent, visualize=visualize)

    def _solve(self, json_data):
        """
        This function needs to get implemented. Currently the only behavior is to end the round.
        :param json_data: raw data for the current round
        :return: operation applied for this round
        """
        return operations.end_round()
