"""
This file provides all necessary information about the possible operations / answers
you can give to a game state (initial and per round prices) as well as the functions
themselves.
"""

# This list contains all possible operation names
OPERATIONS = ["end_round",
              "put_under_quarantine",
              "close_airport",
              "close_connection",
              "develop_vaccine",
              "deploy_vaccine",
              "develop_medication",
              "deploy_medication",
              "exert_influence",
              "call_elections",
              "apply_hygienic_measures",
              "launch_campaign"]

# Dict containing all prices
PRICES = {
    "end_round": {"initial": 0, "each": 0},
    "put_under_quarantine": {"initial": 20, "each": 10},
    "close_airport": {"initial": 15, "each": 5},
    "close_connection": {"initial": 3, "each": 3},
    "develop_vaccine": {"initial": 40, "each": 0},
    "deploy_vaccine": {"initial": 5, "each": 0},
    "develop_medication": {"initial": 20, "each": 0},
    "deploy_medication": {"initial": 10, "each": 0},
    "exert_influence": {"initial": 3, "each": 0},
    "call_elections": {"initial": 3, "each": 0},
    "apply_hygienic_measures": {"initial": 3, "each": 0},
    "launch_campaign": {"initial": 3, "each": 0}
}


def end_round():
    return {"type": "endRound"}


def put_under_quarantine(city, rounds):
    return {"type": "putUnderQuarantine", "city": city, "rounds": rounds}


def close_airport(city, rounds):
    return {"type": "closeAirport", "city": city, "rounds": rounds}


def close_connection(from_city, to_city, rounds):
    return {"type": "closeConnection", "fromCity": from_city, "toCity": to_city, "rounds": rounds}


def develop_vaccine(pathogen):
    return {"type": "developVaccine", "pathogen": pathogen}


def deploy_vaccine(pathogen, city):
    return {"type": "deployVaccine", "pathogen": pathogen, "city": city}


def develop_medication(pathogen):
    return {"type": "developMedication", "pathogen": pathogen}


def deploy_medication(pathogen, city):
    return {"type": "deployMedication", "pathogen": pathogen, "city": city}


def exert_influence(city):
    return {"type": "exertInfluence", "city": city}


def call_elections(city):
    return {"type": "callElections", "city": city}


def apply_hygienic_measures(city):
    return {"type": "applyHygienicMeasures", "city": city}


def launch_campaign(city):
    return {"type": "launchCampaign", "city": city}


def get_operation(op_tuple):
    """
    This function returns an operation by tuple in order to be able to rank these in strategies
    """
    name, *args = op_tuple
    if len(args) > 0:
        return globals()[name](*args)
    else:
        return globals()[name]()
