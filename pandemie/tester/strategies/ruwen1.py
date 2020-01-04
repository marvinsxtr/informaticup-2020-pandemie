from pandemie.tester import AbstractStrategy
from pandemie.util import operations
import random


class Ruwen1(AbstractStrategy):
    def __init__(self, silent=False, visualize=False):
        super().__init__(silent=silent, visualize=visualize)

    def _solve(self, data):
        pathogen = []
        develop = []
        available = []
        if "error" in data:
            print(data["error"])

        # Print("Round:\t", data["round"])
        points = int(data["points"])
        spend = 0

        if "events" in data:
            for event in data["events"]:
                if "pathogen" in event:
                    name = event["pathogen"]["name"]
                else:
                    continue
                if event["type"] == "pathogenEncountered":
                    pathogen.append(name)
                if event["type"] == "medicationInDevelopment":
                    develop.append(name)
                    if name in pathogen:
                        pathogen.remove(name)
                    if name in available:
                        available.remove(name)
                if event["type"] == "medicationAvailable":
                    if name in develop:
                        develop.remove(pathogen)
                    if name in pathogen:
                        pathogen.remove(name)
                    available.append(name)

        if pathogen and points >= operations.PRICES["develop_medication"]["initial"]:
            if not available or random.random() > 0.6:
                spend += operations.PRICES["develop_medication"]["initial"]
                p = random.choice(pathogen)
                pathogen.remove(p)
                op = operations.develop_medication(p)
                return op
        pa = ""
        if available:
            pa = random.choice(available)
        possible = []

        for city in data["cities"]:
            if "events" in data["cities"][city]:
                for event in data["cities"][city]["events"]:
                    if event["type"] == "outbreak":
                        if event["pathogen"]["name"] == pa:
                            possible.append(city)

        if points - spend >= operations.PRICES["deploy_medication"]["initial"] and possible:
            op = operations.deploy_medication(pa, random.choice(possible))
            return op

        return operations.end_round()
