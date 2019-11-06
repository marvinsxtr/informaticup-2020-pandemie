import os.path
from pandemie.util.encoding import filter_unicode
# todo: maybe use pickle to store the data on disk


class EventChecker:
    name_path = "data/event_names.dat"
    pathogen_path = "data/pathogen_names.dat"

    def __init__(self):
        self.events = []
        self.pathogens = []
        self.load_known_events()
        self.load_known_pathogens()

    # Function to load all known event-types
    def load_known_events(self):
        if os.path.exists(self.name_path):
            with open(self.name_path, "r") as f:
                self.events = f.read().split("\n")

    # Function to load all known pathogens
    def load_known_pathogens(self):
        if os.path.exists(self.pathogen_path):
            with open(self.pathogen_path, "r") as f:
                self.pathogens = f.read().split("\n")

    # Function to check if new events occurred
    def check_events(self, events, local):
        for event in events:
            if not event["type"] in self.events:
                self.save_event(event, local)

    # Function to save new events to the data-files
    def save_event(self, event, addition):
        self.events.append(event["type"])

        # Update the names file
        with open(self.name_path, "a") as f:
            f.write("\n" + event["type"])

        # Update the data file
        with open("data/event_data.dat", "a") as f:
            f.write("\n\n{0}\t, {1}\n{2}".format(event["type"], addition, filter_unicode(event)))

    # Function to save pathogens to a file
    def save_pathogen(self, pathogen):
        self.pathogens.append(pathogen["name"])

        with open(self.pathogen_path, "a") as f:
            f.write("\n" + filter_unicode(pathogen["name"]))

        with open("data/pathogen_data.dat", "a") as f:
            f.write(filter_unicode("\n\n{0}\n{1}".format(pathogen["name"], str(pathogen))))

    # TODO: recognize known pathogens, compare not only by name but by attributes
    # Function to check for new pathogens
    def check_for_pathogen(self, events):
        for event in events:
            if event["type"] == "pathogenEncountered":

                # Check if pathogen is known
                for pathogen in self.pathogens:
                    if filter_unicode(event["pathogen"]["name"]) == filter_unicode(pathogen):
                        break
                else:
                    # todo(Ruwen): fix this
                    # Need to be here -> sometimes doesn't detect correct  (Still not correct!)
                    if not event["pathogen"]["name"] in self.pathogens and not \
                                    filter_unicode(event["pathogen"]["name"]) in self.pathogens:
                        self.save_pathogen(event["pathogen"])

    # Function to go through all data to check for events
    def check_all_events(self, data):
        for city in data["cities"]:
            if "events" in data["cities"][city]:
                self.check_events(data["cities"][city]["events"], "local")

        # Check for global events
        if "events" in data:
            self.check_events(data["events"], "global")
            self.check_for_pathogen(data["events"])
