from Controller.Caculations.pie_chart import create_pie_chart


class UIConfig:
    # Font configurations for various UI elements
    FONT = ("Helvetica", 16)                 # Standard text font
    LABEL_FONT = ("Corbel", 20, "bold")     # Font for labels
    INFO_FONT = ("Cambria Math", 14)         # Font for informational text
    BUTTON_FONT = ("Cascadia Code", 16, "bold")  # Font for buttons

    # Color schemes used throughout the UI
    BUTTON_COLOR = ("#000000", "#AEDFF7")   # (text color, background color) for buttons
    INPUT_BG = "#F0F8FF"                     # Background color for input fields
    MULTILINE_BG = "#FFFFFF"                 # Background color for multiline text areas
    MULTILINE_TEXT = "#000000"               # Text color for multiline areas

    # Climbing grade scales
    # Top-rope / sport grades: 5.6 through 5.12d
    GRADES_ROPE = [
        f"5.{i}" if i < 10 else f"5.1{i - 10}{l}"
        for i in range(6, 13) for l in ['a', 'b', 'c', 'd']
    ][:17]
    # Bouldering grades: V0 through V10
    GRADES_BOULDERING = [f"V{i}" for i in range(11)]


def _generate_sample_chart():
    """
    Generate a default pie chart for initial display when no real data is available.
    This done for pie chart before any search has been run
    Returns the PNG image bytes from create_pie_chart.
    """
    data = [20, 20, 20, 20, 20]  # even slices summing to 100%
    title = "Default"           # placeholder chart title
    return create_pie_chart(data, title)
