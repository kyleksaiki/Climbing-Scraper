import PySimpleGUI as sg
# Import UI configuration for fonts and colors, and helper to generate chart images
from View.layouts.ui_config import UIConfig, _generate_sample_chart

# Set the overall theme for the PySimpleGUI window
sg.theme("BlueMono")

# Layout definition for the "Save" tab (TAB_NUM = "2")
save_layout = [
    [  # First row: controls and logo
        sg.Column([  # Left column: buttons and dropdown
            [  # Row of: Load DB button, saved climbs combo, Show Info button
                sg.Button(
                    "Load Database",
                    key="2:Load_DB",
                    font=UIConfig.BUTTON_FONT,
                    button_color=("#000000", "#9694f2")  # black text, light purple background
                ),
                sg.Combo(
                    ["Nothing Loaded"],  # initial dropdown items
                    default_value='Nothing Loaded',
                    key="2:COMBO_SAVE"
                ),
                sg.Button(
                    "Show Info",
                    key="2:Show_Info",
                    font=UIConfig.BUTTON_FONT,
                    button_color=("#000000", "#cffa89")  # black text, light green background
                ),
            ],
            [  # Row of: Delete Entry button
                sg.Button(
                    "Delete Entry",
                    key="-Delete_Entry-",
                    font=UIConfig.BUTTON_FONT,
                    button_color=("#000000", "#f29e9e")  # black text, light red background
                ),
            ],
        ]),
        sg.Push(),  # spacer to push the next element (logo) to the right
        sg.Image(
            filename="logo/Saiki_Lookup.png",  # application logo
            key="2:IMAGE"
        )
    ],
    [  # Second row: text displays for area info and weather
        sg.Multiline(
            key="2:AREA_BASIC",
            font=UIConfig.FONT,
            background_color=UIConfig.MULTILINE_BG,
            text_color=UIConfig.MULTILINE_TEXT,
            size=(30, 20),
            no_scrollbar=True  # hide scrollbar since size is fixed
        ),
        sg.Multiline(
            key="2:WEATHER",
            font=UIConfig.FONT,
            background_color=UIConfig.MULTILINE_BG,
            text_color=UIConfig.MULTILINE_TEXT,
            size=(30, 20)  # weather forecast display
        ),
        sg.Multiline(
            key="2:AREA_DESCRIPTION",
            font=UIConfig.FONT,
            background_color=UIConfig.MULTILINE_BG,
            text_color=UIConfig.MULTILINE_TEXT,
            size=(85, 20)  # area descriptions listing
        ),
        sg.Multiline(
            key="2:AREA_REVIEWS",
            font=UIConfig.FONT,
            background_color=UIConfig.MULTILINE_BG,
            text_color=UIConfig.MULTILINE_TEXT,
            size=(85, 20)  # area comments listing
        )
    ],
    [  # Third row: button to view area photos
        sg.Button(
            "View Photos",
            key="2:PHOTO_OPEN",
            font=UIConfig.BUTTON_FONT,
            button_color=("#000000", "#4d74ee")  # black text, blue background
        )
    ],
    [  # Fourth row: climb info, style chart, descriptions, comments
        sg.Multiline(
            key="2:CLIMB_BASIC",
            font=UIConfig.FONT,
            background_color=UIConfig.MULTILINE_BG,
            text_color=UIConfig.MULTILINE_TEXT,
            size=(30, 20),
            no_scrollbar=True  # basic climb info text area
        ),
        sg.Image(
            key="2:STYLE_CHART",
            data=_generate_sample_chart()  # placeholder for style breakdown chart
        ),
        sg.Multiline(
            key="2:CLIMB_DESCRIPTION",
            font=UIConfig.FONT,
            background_color=UIConfig.MULTILINE_BG,
            text_color=UIConfig.MULTILINE_TEXT,
            size=(85, 20)  # climb descriptions listing
        ),
        sg.Multiline(
            key="2:CLIMB_COMMENTS",
            font=UIConfig.FONT,
            background_color=UIConfig.MULTILINE_BG,
            text_color=UIConfig.MULTILINE_TEXT,
            size=(85, 20)  # climb comments listing
        )
    ]
]
