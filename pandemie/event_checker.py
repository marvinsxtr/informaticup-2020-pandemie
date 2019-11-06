class EventChecker:
    def __init__(self):
        # Init known events
        self.events = None
        self.pathogens = None
        self.load_known_events()
        self.load_known_pathogens()

    # Function to load all known event-types
    def load_known_events(self):
        with open("data/event_names.dat", "r") as f:  # Load known events from data file
            data = f.read()
            # Split the lines -> extract all different events
            names = data.split("\n")
        self.events = names

    # Function to load all known pathogens
    def load_known_pathogens(self):
        with open("data/event_names.dat", "r") as f:  # Load known pathogens from data file
            data = f.read()
            # Split the lines -> extract all different pathogens
            names = data.split("\n")
        self.pathogens = names

    # Function to check if new events occurred
    def check_events(self, events, local):
        for event in events:
            if not event["type"] in self.events:  # Check for unknown events
                self.save_event(event, local)  # New event -> save it

    # Function to save new events to the data-files
    def save_event(self, event, addition):
        self.events.append(event["type"])
        with open("data/event_names.dat", "a") as f:  # Update the names file
            f.write("\n" + event["type"])

        with open("data/event_data.dat", "a") as f:  # Update the data file
            data = "\n\n" + event["type"] + "\t, " + \
                addition + "\n"  # Name and local/global
            data += str(event)  # Example for the structure
            # print(data)
            f.write(data)

    def save_pathogen(self, pathogen):
        self.pathogens.append(pathogen["name"])
        with open("data/pathogen_names.dat", "a") as f:
            f.write("\n" + pathogen["name"])

        with open("data/pathogen_data.dat", "a") as f:
            data = "\n\n" + pathogen["name"] + "\n"  # Name
            data += str(pathogen)  # Example for the structure
            f.write(data)

    def check_for_pathogen(self, events):
        for event in events:
            if event["type"] == "pathogenEncountered":
                if not event["pathogen"]["name"] in self.pathogens:
                    self.save_pathogen(event["pathogen"])

    # Function to go through all data to check for events
    def check_all_events(self, data):
        for city in data["cities"]:  # Check for local events
            if "events" in data["cities"][city]:
                # Event detected -> check if it's known
                self.check_events(data["cities"][city]["events"], "local")

        if "events" in data:  # Check for global events
            # Events detected -> check if it's known
            self.check_events(data["events"], "global")  # Global Event
            self.check_for_pathogen(data["events"])  # Check for pathogens
