
import logging
from typing import Optional
import PySimpleGUI as sg

from Controller.search_tab import SearchTab
from Controller.save_tab import SaveTab
from Model.database import Database
from View.app_gui import View

# Window metadata identifiers
META_MAIN = "Main"
META_IMAGE = "Image"

class Controller:
    """
    Main controller handling the GUI event loop. Mostly handles exits
    and delegating event handling to SearchTab and SaveTab,
    and managing the database connection.
    """

    def __init__(self, view: View) -> None:
        """
        Initialize the Controller with the main application view.
        View is the User interface

        Args:
            view (sg.Window): The primary PySimpleGUI window instance.
        """
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s: %(message)s"
        )

        self.view = view
        self.db = Database()
        self.search_tab = SearchTab(self.view, self.db)
        self.save_tab = SaveTab(self.view, self.db)

    def run(self) -> None:
        """
        Connect to the database and enter the main event loop.
        """
        self.db.connect_to_database()
        try:
            while True:
                window, event, values = sg.read_all_windows()

                # Exit if all windows closed
                if window is None:
                    logging.info("All windows closed. Exiting application.")
                    break

                # Handle window close events
                # Program will fully exit in next loop iteration
                if event == sg.WIN_CLOSED:
                    self._handle_window_close(window)
                    continue

                # Delegate to tabs; break if event handled. View each tab class
                # To see how events are handled
                for tab in (self.search_tab, self.save_tab):
                    handled = tab.handle_event(event, values, self.db)
                    if handled:
                        logging.debug("Event '%s' handled by %s", event, tab.__class__.__name__)
                        break
        #If for whatever reason the program crashes, the database connection will close
        finally:
            self._cleanup()

    def _handle_window_close(self, window: sg.Window) -> None:
        """
        Handle close events for image windows and the main window.

        Args:
            window (sg.Window): The window that triggered a close event.
        """
        metadata = getattr(window, "metadata", None)

        if metadata == META_IMAGE:
            # Close any photoviewer in either tab. Resets the variables
            for tab in (self.search_tab, self.save_tab):
                img_win = getattr(tab, "displayed_image_window", None)
                if img_win:
                    img_win.close()
                    tab.displayed_image_window = None
                    tab.displayed_image = None
                    tab.images = None
                    logging.info("Closed image window for %s", tab.__class__.__name__)
                    break

        elif metadata == META_MAIN:
            # Cleanup and close main window
            window.close()
            self.search_tab.clear_images()
            self.save_tab.clear_images()
            self.db.close()
            logging.info("Main window closed, database connection closed.")

    def _cleanup(self) -> None:
        """
        Perform final cleanup when exiting the application.
        """
        try:
            self.db.close()
        except Exception as e:
            logging.warning("Error closing database during cleanup: %s", e)
        logging.info("Cleanup complete. Application terminated.")

