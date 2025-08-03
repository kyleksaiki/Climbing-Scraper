import io
from typing import Sequence, Optional
import matplotlib.pyplot as plt

# Module-level constants, tinkered to fit my display
# adjustments might be necessary to fit in other users screens
LABELS = ["red", "flash", "go", "tr", "os"]
DPI = 100
FIG_SIZE = (4.69, 6.447)  # width × height in inches
AUTOPCT = "%1.1f%%"
START_ANGLE = 90
TEXT_PROPS = {"fontsize": 14}
LABEL_DISTANCE = 1.15
TITLE_FONT_SIZE = 16
SUBPLOT_MARGINS = {"top": 0.90, "left": 0.1, "right": 0.9, "bottom": 0.1}


def create_pie_chart(
    values: Sequence[float],
    title: str = "Source: VL",
    labels: Optional[Sequence[str]] = None
) -> bytes:
    """
    Generate a pie chart PNG for a fixed set of categories.
    These categories describe the difficulty of a climb using climbing lingo:
    Used by GUI to display info to user

    Args:
        values (Sequence[float]):
            Numeric slices for the pie; length must match `labels` length.
        title (str, optional):
            Chart title. Defaults to "Source: VL".
        labels (Sequence[str], optional):
            Names for each slice; defaults to module-level `LABELS`.

    Returns: bytes: Raw PNG image data of the rendered pie chart.

    Raises: ValueError: If `len(values)` does not match `len(labels)`
    This error should not happen and signifies a function usage problem
    """
    # Assigns labels it's default values for climbing
    # My program only uses this default value
    labels = labels or LABELS

    if len(values) != len(labels):
        raise ValueError(
            f"Data length ({len(values)}) does not match number of labels ({len(labels)})."
        )

    # Create figure & axes
    fig, ax = plt.subplots(figsize=FIG_SIZE, dpi=DPI)

    # Draw pie chart
    ax.pie(
        values,
        labels=labels,
        autopct=AUTOPCT,
        startangle=START_ANGLE,
        textprops=TEXT_PROPS,
        labeldistance=LABEL_DISTANCE
    )

    # Title and aspect
    ax.set_title(title, fontsize=TITLE_FONT_SIZE, pad=20)
    ax.axis("equal")  # keep as a circle

    # Adjust margins
    fig.subplots_adjust(**SUBPLOT_MARGINS)

    # Save to in-memory buffer
    buffer = io.BytesIO()
    fig.savefig(buffer, format="PNG", dpi=DPI)
    plt.close(fig)
    buffer.seek(0)
    return buffer.read()
