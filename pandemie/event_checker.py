import os.path
from pandemie.util.encoding import filter_unicode


class EventChecker:
    """
    Module to check in a given dataset for new event-types
    """
    name_path = "data/event_names.dat"
    pathogen_path = "data/pathogen_names.dat"

    def __init__(self):
        self.events = []
        self.pathogens = []
        # Preload all known events from save-file
        self.load_known_events()
        # Preload all known pathogens from save-file
        self.load_known_pathogens()

    def load_known_events(self):
        """
        Function to load all known event-types from the save-file
        """
        # Check if there is a save-file
        if os.path.exists(self.name_path):
            with open(self.name_path, "r") as f:
                # Load all Lines and split at the end of line
                self.events = f.read().split("\n")

    def load_known_pathogens(self):
        """
        Function to load all known pathogen-types from the save-file
        """
        # Check if there is a save-file
        if os.path.exists(self.pathogen_path):
            with open(self.pathogen_path, "r") as f:
                # Load all Lines and split at the end of line
                self.pathogens = f.read().split("\n")

    def check_events(self, events, local):
        """
        Function to check if new events occurred
        :param events: dict: All events occurred in this round
        :param local: str: Whether the event is "global" or "local"
        """
        # Check if there are unknown events and save them
        for event in events:
            if not event["type"] in self.events:
                self.save_event(event, local)

    def save_event(self, event, addition):
        """
        Function to save a newly occurred event
        :param event: dict: The event to be saved
        :param addition: str: Addition if event is "global" or "local"
        """
        if os.path.exists(self.name_path):
            # Save event locally
            self.events.append(event["type"])

            # Update the names file
            with open(self.name_path, "a") as f:
                # Remove non-printable characters
                f.write("\n" + filter_unicode(event["type"]))

            # Update the data file
            with open("data/event_data.dat", "a") as f:
                # Write example of the event to save-file (Remove non-printable characters)
                f.write("\n\n{0}\t, {1}\n{2}".format(filter_unicode(event["type"]), addition, filter_unicode(event)))

    def save_pathogen(self, pathogen):
        """
        Function to save new discovered pathogens
        :param pathogen: The pathogen to be saved
        """
        if os.path.exists(self.pathogen_path):
            # Save pathogen locally
            self.pathogens.append(filter_unicode(pathogen["name"]).strip())

            # Update the names file
            with open(self.pathogen_path, "a") as f:
                f.write("\n" + filter_unicode(pathogen["name"]).strip())

            # Update the data file
            with open("data/pathogen_data.dat", "a") as f:
                f.write(filter_unicode("\n\n{0}\n{1}".format(pathogen["name"], str(pathogen))))

    def check_for_pathogen(self, events):
        """
        Function to check for new pathogens
        :param events: dict: All occurred events
        """
        for event in events:
            # Check if it's a new pathogen
            if event["type"] == "pathogenEncountered":

                # Check if pathogen is known
                for pathogen in self.pathogens:
                    if filter_unicode(event["pathogen"]["name"]).strip() == pathogen.strip():
                        break
                else:
                    self.save_pathogen(event["pathogen"])

    def parse_data(self, data):
        """
        Function to parse the hole data-set to check for new events and pathogens
        :param data: dict: The complete data-set of the current game-round
        """
        # Check for local events
        for city in data["cities"]:
            if "events" in data["cities"][city]:
                self.check_events(data["cities"][city]["events"], "local")

        # Check for global events and pathogens
        if "events" in data:
            self.check_events(data["events"], "global")
            self.check_for_pathogen(data["events"])
