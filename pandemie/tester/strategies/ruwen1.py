from pandemie.tester import AbstractStrategy
from pandemie.util import operations
import random


class Ruwen1(AbstractStrategy):
    """
    This class is an implementation of strategy.py
    The basic idea of this strategy is to only develop and deploy medication for the occurred pathogens
    """
    def __init__(self, silent=False, visualize=False):
        super().__init__(silent=silent, visualize=visualize)

    def _solve(self, data):
        """
        Function to decide the operation used in the current round
        :param data: raw data for the current round
        :return: operation applied for this round
        """
        pathogen = []
        develop = []
        available = []
        # Print the occurred error
        if "error" in data:
            print(data["error"])

        # Print("Round:\t", data["round"])
        points = int(data["points"])
        spend = 0

        if "events" in data:
            for event in data["events"]:
                # Check the data for pathogens
                if "pathogen" in event:
                    name = event["pathogen"]["name"]
                else:
                    continue
                # Check for new pathogens
                if event["type"] == "pathogenEncountered":
                    pathogen.append(name)
                # Check for medication in development
                if event["type"] == "medicationInDevelopment":
                    develop.append(name)
                    # Remove from pathogens -> Already Medication in development
                    if name in pathogen:
                        pathogen.remove(name)
                    # Theoretically impossible, but who knows
                    if name in available:
                        available.remove(name)
                # Check for finished medication
                if event["type"] == "medicationAvailable":
                    # Removed from in development -> already finished
                    if name in develop:
                        develop.remove(pathogen)
                    # Remove from pathogens -> already medication available
                    if name in pathogen:
                        pathogen.remove(name)
                    available.append(name)

        # Affordable to develop medication?
        if pathogen and points >= operations.PRICES["develop_medication"]["initial"]:
            # If there is already some medication -> 60% chance to start new medication
            if not available or random.random() > 0.6:
                spend += operations.PRICES["develop_medication"]["initial"]
                # Select random pathogen
                p = random.choice(pathogen)
                pathogen.remove(p)
                op = operations.develop_medication(p)
                return op

        # Choose random from available medication
        pa = ""
        if available:
            pa = random.choice(available)
        possible = []

        # Get all cities where the pathogen occurred
        for city in data["cities"]:
            if "events" in data["cities"][city]:
                for event in data["cities"][city]["events"]:
                    if event["type"] == "outbreak":
                        if event["pathogen"]["name"] == pa:
                            possible.append(city)

        # Check if enough points are available
        if points - spend >= operations.PRICES["deploy_medication"]["initial"] and possible:
            # Choose a random city to deploy the medication
            op = operations.deploy_medication(pa, random.choice(possible))
            return op

        return operations.end_round()
