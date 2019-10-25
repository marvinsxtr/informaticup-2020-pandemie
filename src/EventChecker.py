class EventChecker:
    def __init__(self):
        self.events = None
        self.load_known_events()

    def load_known_events(self):
        with open("event_names.dat", "r") as f:
            data = f.read()
            names = data.split("\n")
        self.events = names

    def check_events(self, events, local):
        for event in events:
            if not event["type"] in self.events:
                self.save_event(event, local)

    def save_event(self, event, addition):
        self.events.append(event["type"])
        with open("event_names.dat", "a") as f:
            f.write("\n" + event["type"])

        with open("event_data.dat", "a") as f:
            data = "\n\n" + event["type"] + "\t, " + addition + "\n"
            data += str(event)
            # print(data)
            f.write(data)

    def check_all_events(self, data):
        for city in data["cities"]:
            if "events" in data["cities"][city]:
                self.check_events(data["cities"][city]["events"], "local")

        if "events" in data:
            self.check_events(data["events"], "global")
