from pandemie.tester import AbstractStrategy
from pandemie import operations
import random


class Ruwen1(AbstractStrategy):
    def __init__(self, name, silent=False):
        super().__init__(name, silent=silent)
        self.pathogen = []
        self.develop = []
        self.available = []

    def _solve(self, data, server):
        if "error" in data:
            print(data["error"])

        points = int(data["points"])
        spend = 0

        if "events" in data:
            for event in data["events"]:
                if event["type"] == "pathogenEncountered" and event["round"] == data["round"]:
                    self.pathogen.append(event["pathogen"]["name"])
                if event["type"] == "medicationInDevelopment" and event["pathogen"]["name"] not in self.develop:
                    self.develop.append(event["pathogen"]["name"])
                if event["type"] == "medicationAvailable" and event["pathogen"]["name"] not in self.available:
                    if event["pathogen"]["name"] in self.develop:
                        self.develop.remove(event["pathogen"]["name"])
                    self.available.append(event["pathogen"]["name"])

        if len(self.pathogen) > 0 and points >= operations.PRICES["develop_medication"]["initial"]:
            if (len(self.develop) == 0 and len(self.available) == 0) or random.random() > 0.6:
                spend += operations.PRICES["develop_medication"]["initial"]
                op = operations.develop_medication(random.choice(self.pathogen))
                print(op)
                return op
        pathogen = ""
        if len(self.available) > 0:
            pathogen = random.choice(self.available)
        possible = []

        for city in data["cities"]:
            if "events" in data["cities"][city]:
                for event in data["cities"][city]["events"]:
                    if event["type"] == "outbreak":
                        if event["pathogen"]["name"] == pathogen:
                            break

        if points - spend >= operations.PRICES["deploy_medication"]["initial"] and len(possible) > 0:
            op = operations.deploy_medication(pathogen, random.choice(possible))
            print(op)
            return op

        print("endRound")
        return operations.end_round()
