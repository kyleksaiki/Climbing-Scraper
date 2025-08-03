import logging
from typing import Any, Optional, List, Dict
import PySimpleGUI as sg

from Controller.tab import Tab
from View.app_gui import View
from View.photo_viewer import create_photo_window, update_photo
from Model.database import Database
from Model.climb import Climb

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

class SaveTab(Tab):
    """
    Controller for the Save tab: manages saved climbs, displays info,
    and handles photo viewing for a selected climb.
    """
    IMG_FOLDER = "saved_images"
    TAB_NUM = "2"

    def __init__(self, view: View, db: Database) -> None:
        """
        Initialize the SaveTab with the main GUI view and database.

        Args:
            view (sg.Window): The main application window or tab group.
            db (Database):   Database instance for persistence operations.
        """
        super().__init__(view, db)
        self.current_climb: Optional[Climb] = None
        self.images: Optional[List[str]] = None
        self.image_ind: int = 0
        self.displayed_image_window: Optional[sg.Window] = None
        self.displayed_image: Optional[Any] = None

    def handle_event(self, event: str, values: Dict[str, Any], db: Database) -> bool:
        """
        Handle events emitted from the Save tab.

        Args:
            event (str):  The event key triggered.
            values (dict): The current input values from the window.
            db (Database): Database instance (same as self.db).

        Returns:
            bool: True if the event was handled here; False otherwise.
        """
        # Load saved climbs into the dropdown/list
        if event == f"{self.TAB_NUM}:Load_DB":
            climb_names = self.db.get_all_saved_climb_names()
            self.view.update_saved_climbs(climb_names)
            return True

        # Show detailed info for a selected climb
        elif event == f"{self.TAB_NUM}:Show_Info":
            cid = self.view.get_inputs_save_page(values)
            if cid is None:
                return True
            area, climb = self.db.gather_climb_info(cid)
            self.update_display(area, climb)
            self.current_climb = climb
            return True

        # Open photo viewer for current climb
        elif event == f"{self.TAB_NUM}:PHOTO_OPEN":
            self.load_images(self.current_climb)
            if not self.images:
                self.view.show_popup("No images")
                return True
            self.image_ind = 0
            self.displayed_image_window, self.displayed_image = create_photo_window(
                self.images[self.image_ind]
            )
            return True

        # Navigate to next photo
        elif event == "-PHOTO_NEXT-" and self.displayed_image:
            self._next_photo()
            return True

        # Navigate to previous photo
        elif event == "-PHOTO_PREV-" and self.displayed_image:
            self._prev_photo()
            return True

        # Delete the selected climb entry
        elif event == "-Delete_Entry-":
            cid = self.view.get_inputs_save_page(values)
            if cid is None:
                return True
            self.db.delete_saved_climb(cid)
            return True

        return False

    def _next_photo(self) -> None:
        """
        Move to the next image in the slideshow and update the display.
        """

        self.image_ind = (self.image_ind + 1) % len(self.images)  # type: ignore
        update_photo(self.displayed_image, self.images[self.image_ind])
        logging.debug("Displayed next photo index=%d", self.image_ind)

    def _prev_photo(self) -> None:
        """
        Move to the previous image in the slideshow and update the display.
        """
        self.image_ind = (self.image_ind - 1) % len(self.images)  # type: ignore
        update_photo(self.displayed_image, self.images[self.image_ind])
        logging.debug("Displayed previous photo index=%d", self.image_ind)
