import string


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
            f.write(data)

    # FUnction to save pathogens to a file
    def save_pathogen(self, pathogen):
        self.pathogens.append(pathogen["name"])
        with open("data/pathogen_names.dat", "a") as f:
            f.write("\n" + "".join(x for x in pathogen["name"] if x in string.printable))  # Write name to file

        with open("data/pathogen_data.dat", "a") as f:
            data = "\n\n" + pathogen["name"] + "\n"  # Name
            data += str(pathogen)  # Example for the structure
            data = "".join(x for x in data if x in string.printable)
            f.write(data)

    # Function to check for new pathogens
    def check_for_pathogen(self, events):  # TODO Überarbeite: bekannte pathogene erkennen, Nicht anhand des namens sondern auch anhand der eigenschaften vergleichen
        for event in events:
            if event["type"] == "pathogenEncountered":
                inside = False
                for pathogen in self.pathogens:  # Check if pathogen is known
                    if "".join(x for x in event["pathogen"]["name"] if x in string.printable) == "".join(x for x in pathogen if x in string.printable):
                        inside = True
                        break
                if not inside:
                    # Need to be here -> sometimes doesn't detect correct  (Still not correct!)
                    if not event["pathogen"]["name"] in self.pathogens and not "".join(x for x in event["pathogen"]["name"] if x in string.printable) in self.pathogens:
                        self.save_pathogen(event["pathogen"])
                # if not "".join(x for x in event["pathogen"]["name"] if x in string.printable) in self.pathogens:
                #     self.save_pathogen(event["pathogen"])

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
