from Controller.Caculations.weather import get_weather_forecast


class ClimbingArea:
    def __init__(self, aid = None, state = None, name = None, lat = None, long = None, mt_proj_link = None):
        # Unique area identifier
        self.aid = aid
        # State in which the climbing area is located
        self.state = state
        # Name of the climbing area
        self.name = name
        # Latitude coordinate of the area center
        self.lat = lat
        # Longitude coordinate of the area center
        self.long = long
        # Mountain Project URL for the area
        self.mt_proj_link = mt_proj_link
        # Descriptive texts from Mountain Project
        self.mp_descriptions = []
        # User comments on the area from Mountain Project
        self.mp_area_comments = []
        # List of Climb objects associated with this area
        self.climbs = []

    # Testing: basic area info output
    def string_basic_info(self):
        # Header for basic info
        text = "Basic Info\n"
        # Separator line
        text += f"{'-' * 50}\n"
        # Area name and coordinates
        text += f"Name:\n{self.name}\n\nCoordinates:\n{self.lat} {self.long}\n"
        return text

    # Fetch and return a weather forecast string
    def string_weather(self):
        # Use helper to call the weather API and format output
        return get_weather_forecast(self.lat, self.long)

    # Format all area descriptions into a single block
    def string_area_descriptions(self):
        # Header with count of descriptions
        text = f"Area Descriptions from MP ({len(self.mp_descriptions)}):\n"
        # Long separator for readability
        text += f"{'-' * 141}\n"
        # Append each description in quotes with blank line separators
        for d in self.mp_descriptions:
            text += f"\"{d}\"\n\n"
        return text

    # Format all area comments into a single block
    def string_area_comments(self):
        # Header with count of comments
        text = f"Area Comments ({len(self.mp_area_comments)}):\n"
        # Separator line
        text += f"{'-' * 133}\n"
        # Append each comment in quotes with blank line separators
        for c in self.mp_area_comments:
            text += f"\"{c}\"\n\n"
        return text
