import PySimpleGUI as sg
# Import UI configuration for fonts, colors, and helper to generate chart images
from Controller.Caculations.pie_chart import create_pie_chart
from View.layouts.ui_config import UIConfig, _generate_sample_chart

# Set the overall theme for the PySimpleGUI window
sg.theme("BlueMono")

# Layout definition for the "Search" tab (TAB_NUM = "1")
search_layout = [
    [  # First row: input controls and logo
        sg.Column([  # Left column: label-input pairs and sliders
            [  # Row of: Latitude, Longitude, and distance slider
                sg.Text(
                    "Latitude:",
                    font=UIConfig.LABEL_FONT  # label font from UIConfig
                ),
                sg.Input(
                    key="1:LATITUDE",  # key for event handling
                    size=(30, 1),
                    font=UIConfig.LABEL_FONT,
                    background_color=UIConfig.INPUT_BG  # background color
                ),
                sg.Text(
                    "Longitude:",
                    font=UIConfig.LABEL_FONT
                ),
                sg.Input(
                    key="1:LONGITUDE",
                    size=(30, 1),
                    font=UIConfig.LABEL_FONT,
                    background_color=UIConfig.INPUT_BG
                ),
                sg.Text(
                    "Miles Away:",
                    font=UIConfig.LABEL_FONT
                ),
                sg.Slider(
                    range=(0, 500),  # slider range in miles
                    default_value=60,  # initial distance value
                    orientation="h",  # horizontal slider
                    key="1:DISTANCE",  # key for event handling
                    size=(40, 20),
                    font=UIConfig.FONT
                )
            ],
            [  # Row of: Climbing type dropdown and grade selectors
                sg.Text(
                    "Climbing Type:",
                    font=UIConfig.LABEL_FONT
                ),
                sg.Combo(
                    ["Top Rope", "Bouldering", "All"],  # options
                    default_value="All",
                    key="1:CLIMBING_TYPE",
                    enable_events=True,  # trigger event on change
                    readonly=True,
                    font=UIConfig.LABEL_FONT,
                    size=(20, 1),
                    background_color=UIConfig.INPUT_BG
                ),
                sg.Text(
                    "Min Top Rope:",
                    font=UIConfig.LABEL_FONT,
                    key="1:MIN_TOP_ROPE_LABEL"  # label key
                ),
                sg.Combo(
                    UIConfig.GRADES_ROPE,  # rope grade list
                    default_value="5.6",
                    key="1:MIN_TOP_ROPE",
                    size=(8, 1),
                    readonly=True,
                    font=UIConfig.LABEL_FONT,
                    background_color=UIConfig.INPUT_BG
                ),
                sg.Text(
                    "Max Top Rope:",
                    font=UIConfig.LABEL_FONT,
                    key="1:MAX_TOP_ROPE_LABEL"
                ),
                sg.Combo(
                    UIConfig.GRADES_ROPE,
                    default_value="5.12d",
                    key="1:MAX_TOP_ROPE",
                    size=(8, 1),
                    readonly=True,
                    font=UIConfig.LABEL_FONT,
                    background_color=UIConfig.INPUT_BG
                ),
                sg.Text(
                    "Min Bouldering:",
                    font=UIConfig.LABEL_FONT,
                    key="1:MIN_BOULDERING_LABEL"
                ),
                sg.Combo(
                    UIConfig.GRADES_BOULDERING,  # bouldering grade list
                    default_value="V0",
                    key="1:MIN_BOULDERING",
                    size=(6, 1),
                    readonly=True,
                    font=UIConfig.LABEL_FONT,
                    background_color=UIConfig.INPUT_BG
                ),
                sg.Text(
                    "Max Bouldering:",
                    font=UIConfig.LABEL_FONT,
                    key="1:MAX_BOULDERING_LABEL"
                ),
                sg.Combo(
                    UIConfig.GRADES_BOULDERING,
                    default_value="V10",
                    key="1:MAX_BOULDERING",
                    size=(6, 1),
                    readonly=True,
                    font=UIConfig.LABEL_FONT,
                    background_color=UIConfig.INPUT_BG
                )
            ],
            [  # Row of: Search and Generate Database buttons
                sg.Button(
                    "Search",
                    key="1:SEARCH",
                    font=UIConfig.BUTTON_FONT,
                    button_color=("#000000", "#cffa89")  # black text on light green
                ),
                sg.Button(
                    "Generate Database",
                    key="1:GENERATE_DB",
                    font=UIConfig.BUTTON_FONT,
                    button_color=("#000000", "#9694f2")  # black text on light purple
                )
            ],
            [  # Row of: Prev/Next Area and Save Climb buttons
                sg.Button(
                    "Prev Area",
                    key="1:PREV_AREA",
                    font=UIConfig.BUTTON_FONT,
                    button_color=("#000000", "#f1f695")  # black text on light yellow
                ),
                sg.Button(
                    "Next Area",
                    key="1:NEXT_AREA",
                    font=UIConfig.BUTTON_FONT,
                    button_color=("#000000", "#92f8f6")  # black text on light cyan
                ),
                sg.Button(
                    "Save Climb",
                    key="1:SAVE",
                    font=UIConfig.BUTTON_FONT,
                    button_color=("#000000", "#f29e9e")  # black text on light red
                )
            ],
            [  # Row of: Area info label and counter
                sg.Text(
                    "Area Info:",
                    font=("Helvetica", 16, "bold")
                ),
                sg.Text(
                    "0/0",  # initial counter value
                    key="1:NUM_AREAS",
                    font=("Helvetica", 16, "bold")
                )
            ]
        ]),
        sg.Push(),  # spacer to right-align the logo
        sg.Image(
            filename="logo/Saiki_Search.png",  # search tab logo
            key="1:IMAGE"
        )
    ],
    [  # Second row: displays for area info, weather, descriptions, reviews
        sg.Multiline(
            key="1:AREA_BASIC",
            font=UIConfig.FONT,
            background_color=UIConfig.MULTILINE_BG,
            text_color=UIConfig.MULTILINE_TEXT,
            size=(30, 20),
            no_scrollbar=True
        ),
        sg.Multiline(
            key="1:WEATHER",
            font=UIConfig.FONT,
            background_color=UIConfig.MULTILINE_BG,
            text_color=UIConfig.MULTILINE_TEXT,
            size=(30, 20)
        ),
        sg.Multiline(
            key="1:AREA_DESCRIPTION",
            font=UIConfig.FONT,
            background_color=UIConfig.MULTILINE_BG,
            text_color=UIConfig.MULTILINE_TEXT,
            size=(85, 20)
        ),
        sg.Multiline(
            key="1:AREA_REVIEWS",
            font=UIConfig.FONT,
            background_color=UIConfig.MULTILINE_BG,
            text_color=UIConfig.MULTILINE_TEXT,
            size=(85, 20)
        )
    ],
    [  # Third row: header for climb list
        sg.Text(
            "Climbs in Area (sorted by most popular):",
            font=("Helvetica", 16, "bold")
        ),
        sg.Text(
            "0/0",  # initial climb counter
            key="1:NUM_CLIMBS",
            font=("Helvetica", 16, "bold")
        )
    ],
    [  # Fourth row: Prev/Next Climb and View Photos buttons
        sg.Button(
            "Prev Climb",
            key="1:PREV_CLIMB",
            font=UIConfig.BUTTON_FONT,
            button_color=("#000000", "#f1f695")
        ),
        sg.Button(
            "Next Climb",
            key="1:NEXT_CLIMB",
            font=UIConfig.BUTTON_FONT,
            button_color=("#000000", "#92f8f6")
        ),
        sg.Button(
            "View Photos",
            key="1:PHOTO_OPEN",
            font=UIConfig.BUTTON_FONT,
            button_color=("#000000", "#4d74ee")
        )
    ],
    [  # Fifth row: climb info, style chart, description, comments
        sg.Multiline(
            key="1:CLIMB_BASIC",
            font=UIConfig.FONT,
            background_color=UIConfig.MULTILINE_BG,
            text_color=UIConfig.MULTILINE_TEXT,
            size=(30, 20),
            no_scrollbar=True
        ),
        sg.Image(
            key="1:STYLE_CHART",
            data=_generate_sample_chart()  # initially using sample chart function
        ),
        sg.Multiline(
            key="1:CLIMB_DESCRIPTION",
            font=UIConfig.FONT,
            background_color=UIConfig.MULTILINE_BG,
            text_color=UIConfig.MULTILINE_TEXT,
            size=(85, 20)
        ),
        sg.Multiline(
            key="1:CLIMB_COMMENTS",
            font=UIConfig.FONT,
            background_color=UIConfig.MULTILINE_BG,
            text_color=UIConfig.MULTILINE_TEXT,
            size=(85, 20)
        )
    ]
]