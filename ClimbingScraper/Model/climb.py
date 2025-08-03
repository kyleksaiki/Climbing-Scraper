# Import the function to convert European grades to US grades
from Controller.Caculations.us_to_euro_grading import convert_eu_to_us
# Import the Photo model for handling images
from Model.photo import Photo


class Climb:
    def __init__(self):
        # Identification fields
        self.name = None
        self.type = None
        # Mountain Project data
        self.mp_stars = None            # Numeric star rating from MP
        self.num_mp_stars = None        # Raw string count of MP ratings
        self.mp_grade = None            # Grade from Mountain Project (YDS)
        self.mp_descriptions = []       # Detailed description texts from MP
        self.mp_comments = []           # User comments from MP
        self.mp_photos = []             # Photo objects associated with MP

        # Vertical-Life data
        self.vl_comments = []           # User comments from VL
        self.vl_ascents = None          # Total ascent count on VL
        self.vl_recommends = None       # Number of “recommends” on VL
        self.vl_onsite_rate = None      # Calculated onsight success rate (%)
        self.vl_style = None            # Breakdown of style counts from VL
        self.vl_grade = None            # Grade from VL (EU system)
        self.vl_stars = None            # Star rating from VL
        self.vl_photos = []             # Photo objects associated with VL

    # Implement to minimize dependency on external code
    def add_photo(self, link, folder):
        # Create a Photo instance and store it in the MP photos list
        # When Photo object is created, it is downloaded in either saved_images or search_images
        self.mp_photos.append(Photo(link, self.name, folder))

    def string_basic_info(self):
        # Build a summary string for basic climb information
        text = "Climb Basic Information:\n"
        text += f"{"-" * 50}\n"
        text += f"Name: {self.name}\nType: {self.type}\n"
        text += f"MP Grade: {self.mp_grade}\n"
        # Convert VL grade to US and show the raw EU grade
        text += f"VL Grade: {convert_eu_to_us(self.vl_grade, self.type)} ({self.vl_grade})\n"
        text += f"VL Onsite Rate: {self.vl_onsite_rate}%\n"
        # Show MP and VL review scores
        text += f"MP Review Score ({self.num_mp_stars}): {self.mp_stars}/5\n"
        text += f"VL Review Score ({self.vl_ascents}): {self.vl_stars}/5\n"
        text += f"VL Recommends: {self.vl_recommends}\n"
        return text

    def get_data_chart(self):
        # Return equal slices if no style data available
        if self.vl_style is None: return [20, 20, 20, 20, 20]
        # Define the order of style categories
        labels = ["redpoint", "flash", "go", "topRope", "onsight"]
        # Extract raw counts in the specified order
        data = [self.vl_style[label] for label in labels]
        # Convert counts to percentage of total ascents
        result = [round(x / self.vl_ascents, 2) * 100 for x in data]
        return result

    def string_descriptions(self):
        # Build a header for MP descriptions
        text = f"Description from MP ({len(self.mp_descriptions)}):\n"
        text += f"{"-" * 133}\n"
        # Append each description, quoted and separated by blank lines
        for d in self.mp_descriptions:
            text += f"\"{d}\"\n\n"
        return text

    def string_comments(self):
        # Header for MP comments
        text = f"Comments from MP ({len(self.mp_comments)}):\n"
        text += f"{"-" * 133}\n"
        # Append each MP comment
        for c in self.mp_comments:
            text += f"\"{c}\"\n\n"
        # Header for VL comments
        text += f"\nComments from VL ({len(self.vl_comments)}):\n"
        text += f"{"-" * 133}\n"
        # Append each VL comment
        for c in self.vl_comments:
            text += f"\"{c}\"\n\n"
        return text
