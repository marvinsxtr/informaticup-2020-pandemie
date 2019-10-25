class EventChecker:
    def __init__(self):
        # Init known events
        self.events = None
        self.load_known_events()

    # Function to load all known event-types
    def load_known_events(self):
        with open("event_names.dat", "r") as f:  # Load known events from data file
            data = f.read()
            names = data.split("\n")  # Split the lines -> extract all diffrent events
        self.events = names

    # Function to check if new events occurred
    def check_events(self, events, local):
        for event in events:
            if not event["type"] in self.events:  # Check for unknown events
                self.save_event(event, local)  # New event -> save it

    # Function to save new events to the data-files
    def save_event(self, event, addition):
        self.events.append(event["type"])
        with open("event_names.dat", "a") as f:  # Update the names file
            f.write("\n" + event["type"])

        with open("event_data.dat", "a") as f:  # Update the data file
            data = "\n\n" + event["type"] + "\t, " + addition + "\n"  # Name and local/global
            data += str(event)  # Example for the structure
            # print(data)
            f.write(data)

    # Function to go through all data to check for events
    def check_all_events(self, data):
        for city in data["cities"]:  # Check for local events
            if "events" in data["cities"][city]:
                self.check_events(data["cities"][city]["events"], "local")  # Event detected -> check if it's known

        if "events" in data:  # Check for global events
            self.check_events(data["events"], "global")  # Events detected -> check if it's known
