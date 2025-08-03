import gc
import logging
import threading
from typing import Any, Dict, List, Optional, Tuple

from Controller.tab import Tab
from Controller.Scrapers.database_initialization import DatabaseInitializationScraper
from Controller.Scrapers.mt_proj_scraper import scrape_mt_proj
from Controller.Scrapers.v_life_scraper import scrape_vertical_life
from Model.climbing_area import ClimbingArea
from Model.database import Database
from View.app_gui import View
from View.photo_viewer import create_photo_window, update_photo

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

# Module-level constants
TAB_NUM = "1"
IMG_FOLDER = "search_images"
GEN_DB_STATE = "california"  # default state for initial database generation

class SearchTab(Tab):
    """
    Controller for the Search tab: handles user inputs, triggers
    area scraping (mountainproject + Vertical-Life), and manages
    navigation and photo viewing for search results.
    """
    TAB_NUM = TAB_NUM
    IMG_FOLDER = IMG_FOLDER

    def __init__(self, view: View, db: Database) -> None:
        """
        Initialize SearchTab with GUI view and database instance.

        Args:
            view: Main application view.
            db:   Connected Database instance.
        """
        super().__init__(view, db)
        self.result_queue: List[Dict[str, Any]] = []
        self.queue_ind: int = 0
        self.images: List[str] = []
        self.image_ind: int = 0
        # Lock protects queue appends from worker threads
        self.lock = threading.Lock()

    def handle_event(self, event: str, values: Dict[str, Any], db: Database) -> bool:
        """
        Dispatch incoming events from the Search tab.

        Returns True if event was handled; False otherwise.
        """
        # Climbing type selection
        if event == f"{self.TAB_NUM}:CLIMBING_TYPE":
            self.view.update_climbing_fields(values[event])
            return True

        # Generate or refresh the database
        if event == f"{self.TAB_NUM}:GENERATE_DB":
            return self._handle_generate_db(db)

        # Perform search and scraping
        if event == f"{self.TAB_NUM}:SEARCH":
            return self._handle_search(values)

        # Save current result to saved climbs
        if event == f"{self.TAB_NUM}:SAVE":
            return self._handle_save()

        # Open photo viewer
        if event == f"{self.TAB_NUM}:PHOTO_OPEN":
            return self._handle_photo_open()

        # Navigate photos
        if event == "-PHOTO_NEXT-" and self.displayed_image:
            return self._next_photo()
        if event == "-PHOTO_PREV-" and self.displayed_image:
            return self._prev_photo()

        # If no results queued, skip further nav handling
        if self.result_queue_size() == 0:
            return False

        # Navigate between areas
        if event == f"{self.TAB_NUM}:PREV_AREA":
            return self._navigate_area(-1)
        if event == f"{self.TAB_NUM}:NEXT_AREA":
            return self._navigate_area(+1)

        # Navigate between climbs within current area
        if event == f"{self.TAB_NUM}:PREV_CLIMB":
            return self._navigate_climb(-1)
        if event == f"{self.TAB_NUM}:NEXT_CLIMB":
            return self._navigate_climb(+1)

        return False

    def _handle_generate_db(self, db: Database) -> bool:
        """
        Initialize the database via scraper if user confirms.
        I have the confirm button, because this process is time-consuming.
        Don't want user to accidentally click this
        """
        if self.view.show_confirmation_pop_up():
            scraper = DatabaseInitializationScraper()
            scraper.scrape_state(GEN_DB_STATE)
            scraper.close()
            logging.info("Database initialized for state: %s", GEN_DB_STATE)
        return True

    def _handle_search(self, values: Dict[str, Any]) -> bool:
        """
        Clear previous results, query DB for areas, and launch
        scraping threads for each area.
        """
        inputs = self.view.get_inputs_search_page(values)
        if inputs is None:
            return True

        lat, lon, dist = inputs
        # Tear down old GUI and clear memory
        # Old window has to be completly close with garbage collect
        # because the pysimple gui does not work well with multithreading
        try:
            self.view.window.close()
        except Exception:
            pass
        gc.collect()

        self.result_queue.clear()
        self.queue_ind = 0
        self.clear_images()
        self.displayed_image = None

        # Fetch raw area objects from DB
        areas = self.db.search_db_for_areas(lat, lon, dist)
        logging.info("Found %d areas, starting scraping threads", len(areas))

        # Prepare threads
        results: List[Optional[ClimbingArea]] = [None] * len(areas)
        def worker(idx: int, area: ClimbingArea) -> None:
            results[idx] = scrape_area_worker(area)
            with self.lock:
                self.result_queue.append({"area": area, "c_index": 0})

        threads = []
        for i, area in enumerate(areas):
            t = threading.Thread(target=worker, args=(i, area), daemon=True)
            t.start()
            threads.append(t)

        for t in threads:
            t.join()
        gc.collect()

        # Rebuild GUI
        self.view = View()
        if not self.result_queue:
            self.view.show_popup("No results found")
        else:
            area, climb = self.result_queue[self.queue_ind]["area"], \
                          self.result_queue[self.queue_ind]["area"].climbs[0]
            self.update_display(area, climb)
        return True

    def _handle_save(self) -> bool:
        """
        Insert the current area/climb into saved climbs in DB.
        """
        area, climb = self.result_queue[self.queue_ind]["area"], \
                      self.result_queue[self.queue_ind]["area"].climbs[
                          self.result_queue[self.queue_ind]["c_index"]
                      ]
        self.db.insert_saved_climb(area, climb)
        logging.info("Saved climb: %s", climb.name)
        return True

    def _handle_photo_open(self) -> bool:
        """
        Display photos for the current climb if available.
        """
        _, climb = self.result_queue[self.queue_ind]["area"], \
                  self.result_queue[self.queue_ind]["area"].climbs[
                      self.result_queue[self.queue_ind]["c_index"]
                  ]
        self.load_images(climb)
        if not self.images:
            self.view.show_popup("No images")
            return True

        self.image_ind = 0
        self.displayed_image_window, self.displayed_image = \
            create_photo_window(self.images[self.image_ind])
        return True

    def _next_photo(self) -> bool:
        """Advance to next photo in current slideshow."""
        self.image_ind = (self.image_ind + 1) % len(self.images)
        update_photo(self.displayed_image, self.images[self.image_ind])
        return True

    def _prev_photo(self) -> bool:
        """Go back to previous photo in current slideshow."""
        self.image_ind = (self.image_ind - 1) % len(self.images)
        update_photo(self.displayed_image, self.images[self.image_ind])
        return True

    def _navigate_area(self, step: int) -> bool:
        """Move to previous or next area based on step (+/-1)."""
        new_idx = self.queue_ind + step
        if 0 <= new_idx < len(self.result_queue):
            self.queue_ind = new_idx
            area = self.result_queue[self.queue_ind]["area"]
            climb = area.climbs[self.result_queue[self.queue_ind]["c_index"]]
            self.update_display(area, climb)
            return True
        return False

    def _navigate_climb(self, step: int) -> bool:
        """Move to previous or next climb in current area."""
        entry = self.result_queue[self.queue_ind]
        idx = entry["c_index"] + step
        climbs = entry["area"].climbs
        if 0 <= idx < len(climbs):
            entry["c_index"] = idx
            self.update_display(entry["area"], climbs[idx])
            return True
        return False


def scrape_area_worker(area: ClimbingArea) -> ClimbingArea:
    """
    Thread worker: scrapes MountainProject then Vertical-Life for a given area.
    """
    scrape_mt_proj(area)
    scrape_vertical_life(area)
    return area
