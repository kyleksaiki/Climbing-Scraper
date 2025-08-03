import PySimpleGUI as sg
from typing import Tuple

def create_photo_window(
    first_image: bytes,
    button_font: Tuple[str, int] = ("Helvetica", 12),
) -> Tuple[sg.Window, sg.Image]:
    """
    Create a modal “Image” window with Prev/Next controls.

    Args:
        first_image: Raw image bytes (PNG/JPEG) to display initially.
        button_font: Font for the Prev/Next buttons.

    Returns:
        A tuple of (Window, ImageElement) so you can update the image later.
    """
    layout = [
        [sg.Image(data=first_image, key='-IMG-')],
        [
            sg.Button('Prev', key='-PHOTO_PREV-', font=button_font, button_color=("#000000", "#f1f695")),
            sg.Button('Next', key='-PHOTO_NEXT-', font=button_font, button_color=("#000000", "#92f8f6")),
        ],
    ]
    window = sg.Window(
        title='Image',
        layout=layout,
        resizable=True,
        modal=True,
        keep_on_top=True,
        finalize=True,
        metadata='Image',
    )
    # Cache the Image element for fast updates
    img_elem = window['-IMG-']
    return window, img_elem

def update_photo(img_elem: sg.Image, img_data: bytes) -> None:
    """
    Swap in new image bytes into an existing Image element.

    Args:
        img_elem: The sg.Image element returned by create_photo_window.
        img_data: New raw image bytes (PNG/JPEG).
    """
    img_elem.update(data=img_data)
    # Process pending GUI events and force redraw
    img_elem.ParentForm.read(timeout=0)
    img_elem.ParentForm.refresh()
