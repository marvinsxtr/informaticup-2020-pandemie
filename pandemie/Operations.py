import json


class Operations:
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

    def end_round(self):
        return json.dumps({"type": "endRound"})

    def close_airport(self, city, rounds):
        return json.dumps({"type": "putUnderQuarantine", "city": city, "rounds": rounds})
