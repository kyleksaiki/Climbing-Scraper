
import os
from pathlib import Path
from typing import List, Optional

import PySimpleGUI as sg
from copy import deepcopy

from Controller.Caculations.pie_chart import create_pie_chart
from View.layouts.save_layout import save_layout
from View.layouts.search_layout import search_layout


class View:
    """
    Main application view using PySimpleGUI. Manages window creation,
    layout building, and UI updates for area/search information.
    """
    BASE_DIR = Path(__file__).resolve().parent
    FONT = ("Helvetica", 20)

    def __init__(self) -> None:
        # Ensure working directory is the script dir for relative paths
        os.chdir(self.BASE_DIR)

        # Build and show the main window with Search/Save tabs
        layout = self._build_layout()
        self.window = sg.Window(
            "Main",
            layout,
            resizable=True,
            finalize=True,
            font=self.FONT,
            location=(0, 0),
            metadata='Main',
            size=sg.Window.get_screen_size()
        )
        self.window.bind("<Configure>", "_WINDOW_RESIZE_")

    def _build_layout(self) -> list:
        # Deep-copy imported layouts to avoid reusing Elements across windows
        search_tab = deepcopy(search_layout)
        save_tab = deepcopy(save_layout)

        tabs = [[
            sg.Tab("Search", search_tab),
            sg.Tab("Saved Results", save_tab)
        ]]
        return [[sg.TabGroup(tabs, expand_x=True, expand_y=True)]]

    def update_climbing_fields(self, climbing_type: str) -> None:
        """Show or hide grade selectors based on climbing_type selection."""
        top_keys = ["1:MIN_TOP_ROPE_LABEL", "1:MIN_TOP_ROPE", "1:MAX_TOP_ROPE_LABEL", "1:MAX_TOP_ROPE"]
        boulder_keys = ["1:MIN_BOULDERING_LABEL", "1:MIN_BOULDERING", "1:MAX_BOULDERING_LABEL", "1:MAX_BOULDERING"]
        top_visible = climbing_type in ("Top Rope", "All")
        boulder_visible = climbing_type in ("Bouldering", "All")
        for k in top_keys:
            self.window[k].update(visible=top_visible)
        for k in boulder_keys:
            self.window[k].update(visible=boulder_visible)

    def show_popup(self, text: str) -> None:
        """Display a simple popup message."""
        sg.popup(text, font=self.FONT)

    def show_confirmation_pop_up(self) -> bool:
        """Modal confirmation before long-running database generation."""
        prev_theme = sg.theme()
        sg.theme('DarkBlue3')
        layout = [
            [sg.Text("⚠️ Warning", font=("Helvetica", 28, "bold"), text_color='yellow')],
            [sg.Text(
                "Generating the database takes an extended period of time.\n"
                "Avoid repeat generations.",
                font=("Helvetica", 20), size=(50, 3), text_color='white'
            )],
            [sg.Text("Proceed?", font=("Helvetica", 20, "italic"), text_color='white')],
            [
                sg.Button("Yes, Proceed", button_color=('white', '#007BFF'), size=(20,2), font=("Helvetica",16)),
                sg.Button("Cancel",       button_color=('white', '#FF4136'), size=(20,2), font=("Helvetica",16))
            ]
        ]
        win = sg.Window("Confirmation Required", layout, keep_on_top=True, modal=True, element_justification='c')
        choice = False
        while True:
            event, _ = win.read()
            if event in (sg.WINDOW_CLOSED, "Cancel"):
                break
            if event == "Yes, Proceed":
                choice = True
                break
        win.close()
        sg.theme(prev_theme)
        return choice

    def update_counters(self, area_count: str, climb_count: str) -> None:
        """Update the area and climb counters in the Search tab."""
        self.window["1:NUM_AREAS"].update(area_count)
        self.window["1:NUM_CLIMBS"].update(climb_count)

    # Generic helper for updating readonly Multiline elements
    def _update_multiline(self, key: str, text: str) -> None:
        elem = self.window[key]
        elem.update(value=text)

    def display_area_basic(self, tab: str, text: str) -> None:
        self._update_multiline(f"{tab}:AREA_BASIC", text)

    def display_area_weather(self, tab: str, text: str) -> None:
        self._update_multiline(f"{tab}:WEATHER", text)

    def display_area_descriptions(self, tab: str, text: str) -> None:
        self._update_multiline(f"{tab}:AREA_DESCRIPTION", text)

    def display_area_comments(self, tab: str, text: str) -> None:
        self._update_multiline(f"{tab}:AREA_REVIEWS", text)

    def display_climb_basic(self, tab: str, text: str) -> None:
        self._update_multiline(f"{tab}:CLIMB_BASIC", text)

    def display_climb_descriptions(self, tab: str, text: str) -> None:
        self._update_multiline(f"{tab}:CLIMB_DESCRIPTION", text)

    def display_climb_comments(self, tab: str, text: str) -> None:
        self._update_multiline(f"{tab}:CLIMB_COMMENTS", text)

    def update_chart(self, tab: str, data) -> None:
        """Generate and display a pie chart for climb style data."""
        self.window[f"{tab}:STYLE_CHART"].update(create_pie_chart(data))

    def update_saved_climbs(self, names: List[str]) -> None:
        """Populate the saved climbs dropdown in the Save tab."""
        values = names or ["Nothing Loaded"]
        self.window["2:COMBO_SAVE"].update(values=values, value=values[0])

    def get_inputs_search_page(self, values: dict) -> Optional[tuple]:
        """Retrieve and validate search parameters (lat, lon, distance)."""
        try:
            return float(values["1:LATITUDE"]), float(values["1:LONGITUDE"]), float(values["1:DISTANCE"])
        except ValueError:
            self.show_popup("Please enter valid numbers for Latitude, Longitude, and Distance")
            return None

    def get_inputs_save_page(self, values: dict) -> Optional[int]:
        """Extract CID from the Save tab dropdown selection."""
        sel = values["2:COMBO_SAVE"]
        if sel == "Nothing Loaded":
            self.show_popup("No climb has been selected")
            return None
        return int(sel.split("CID:", 1)[1].rstrip(')'))
