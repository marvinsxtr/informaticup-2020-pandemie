import json

PRICES = dict({
    "end_round": dict({"initial": 0, "each": 0}),
    "put_under_quarantine": dict({"initial": 20, "each": 10}),
    "close_airport": dict({"initial": 15, "each": 5}),
    "close_connection": dict({"initial": 3, "each": 3}),
    "develop_vaccine": dict({"initial": 40, "each": 0}),
    "deploy_vaccine": dict({"initial": 5, "each": 0}),
    "develop_medication": dict({"initial": 20, "each": 0}),
    "deploy_medication": dict({"initial": 10, "each": 0}),
    "exert_influence": dict({"initial": 3, "each": 0}),
    "call_elections": dict({"initial": 3, "each": 0}),
    "apply_hygienic_measures": dict({"initial": 3, "each": 0}),
    "launch_campaign": dict({"initial": 3, "each": 0})
})


def end_round():
    return json.dumps({"type": "endRound"})


def put_under_quarantaine(city, rounds):
    return json.dumps({"type": "putUnderQuarantine", "city": city, "rounds": rounds})


def close_airport(city, rounds):
    return json.dumps({"type": "closeAirport", "city": city, "rounds": rounds})


def close_connection(from_city, to_city, rounds):
    return json.dumps({"type": "closeConnection", "fromCity": from_city, "toCity": to_city, "rounds": rounds})


def develop_vaccine(pathogen):
    return json.dumps({"type": "developVaccine", "pathogen": pathogen})


def deploy_vaccine(pathogen, city):
    return json.dumps({"type": "deployVaccine", "pathogen": pathogen, "city": city})


def develop_medication(pathogen):
    return json.dumps({"type": "developMedication", "pathogen": pathogen})


def deploy_medication(pathogen, city):
    return json.dumps({"type": "deployMedication", "pathogen": pathogen, "city": city})


def exert_influence(city):
    return json.dumps({"type": "exertInfluence", "city": city})


def call_elections(city):
    return json.dumps({"type": "callElections", "city": city})


def apply_hygienic_measures(city):
    return json.dumps({"type": "applyHygienicMeasures", "city": city})


def launch_campaign(city):
    return json.dumps({"type": "launchCampaign", "city": city})
