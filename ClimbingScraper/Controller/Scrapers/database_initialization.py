import logging
import re
import time
from typing import Optional, Dict, Any

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from Model.database import Database
from urllib.parse import urlparse, parse_qs

# ——— Module-level constants ———
BASE_SEARCH_URL = "https://www.mountainproject.com/search"
SEARCH_TYPE = "areas"
STATES = [
        'alabama', 'alaska', 'arizona', 'arkansas', 'california', 'colorado', 'connecticut', 'delaware',
        'florida', 'georgia', 'hawaii', 'idaho', 'illinois', 'indiana', 'iowa', 'kansas', 'kentucky',
        'louisiana', 'maine', 'maryland', 'massachusetts', 'michigan', 'minnesota', 'mississippi', 'missouri',
        'montana', 'nebraska', 'nevada', 'new+hampshire', 'new+jersey', 'new+mexico', 'new+york',
        'north+carolina', 'north+dakota', 'ohio', 'oklahoma', 'oregon', 'pennsylvania', 'rhode+island',
        'south+carolina', 'south+dakota', 'tennessee', 'texas', 'utah', 'vermont', 'virginia', 'washington'
]
#Adjust this for a more accurate program, most of the time you just
#want all the top climbing areas not all of them
#300 scrolls will give you around 3000 climbing areas per state
MAX_SCROLLS = 300
SCROLL_PAUSE = 1.0  # seconds
PAGE_LOAD_TIMEOUT = 10  # seconds


class DatabaseInitializationScraper:
    """
    Scrapes all climbing areas from Mountain Project for each U.S. state
    and stores them in the local database. This is used to initialize the database
    to allow search to run.
    """

    def __init__(self) -> None:
        self.driver = webdriver.Chrome()
        self.db = Database()
        self.db.connect_to_database()
        #Used for primary key in database
        self._aid_counter = 0

    def close(self) -> None:
        """Shut down WebDriver and database connection."""
        self.driver.quit()
        self.db.close()

    def scrape_all_states(self) -> None:
        """Iterate through all STATES and scrape each one."""
        for state in STATES:
            self.scrape_state(state)

    def scrape_state(self, state: str) -> None:
        """
        Scrape climbing areas for a specific state.

        Args:
            state: State name (e.g. 'california' or 'new+york').
        """
        logging.info("Scraping %s …", state)
        page = self._fetch_page(state)
        self._parse_areas(page, state)

    def _fetch_page(self, state: str) -> BeautifulSoup:
        """
        Load and fully render the search results page for a given state.
        Page hase to be fully loaded for parsing html data
        Args:
            state: State to search by.

        Returns:
            Parsed BeautifulSoup of the loaded page.
        """
        params = {"q": state, "type": SEARCH_TYPE}
        self.driver.get(BASE_SEARCH_URL, params=params)
        # Wait until at least one area result appears
        WebDriverWait(self.driver, PAGE_LOAD_TIMEOUT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/area/']"))
        )
        self._load_all_results()
        return BeautifulSoup(self.driver.page_source, "lxml")

    def _load_all_results(self) -> None:
        """
        Scroll to bottom and click “Load More” until no more results or MAX_SCROLLS reached.
        """
        for _ in range(MAX_SCROLLS):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            try:
                load_btn = WebDriverWait(self.driver, PAGE_LOAD_TIMEOUT).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "(//button[contains(text(), 'Load More')])[2]")
                    )
                )
                load_btn.click()
                logging.debug("Clicked 'Load More'")
            except Exception:
                logging.debug("No more 'Load More' button.")
                break
            time.sleep(SCROLL_PAUSE)

    def _parse_areas(self, soup: BeautifulSoup, state: str) -> None:
        """
        This function is done after the site is fully loaded and html is recived.
        From a search-results soup, find all area links in the given state
        and insert them into the database.

        Args:
            soup: Parsed search-results HTML.
            state: State filter string.
        """
        area_links = soup.find_all("a", href=lambda h: h and "/area/" in h)
        for link_tag in area_links:
            # Verify the area’s state label matches
            state_label = link_tag.find("div", class_="sc-pyfCe hMSYUk")
            if not state_label or state_label.text.lower().strip() != state:
                continue

            parsed = self._parse_area(link_tag["href"])
            if parsed:
                name, lat, lng, url = parsed
                self.db.insert_climb_area(
                    self._aid_counter, name, lat, lng, url, state
                )
                self._aid_counter += 1

    def _parse_area(self, area_url: str) -> Optional[tuple[str, str, str, str]]:
        """
        Fetch the individual climbing area page, validate, and extract details.
        These details are basic details that allow for a more in depth search later on.
        Some climbing areas in Mountain Project are simply composed of many climbing areas.
        To avoid repreat entries, this only stores climbing areas that actually have routes.
        Args:
            area_url: URL path to the area page.
        Returns:
            Tuple of (name, latitude, longitude, full_url) or None if not a valid area.

        """
        full_url = f"https://www.mountainproject.com{area_url}"
        resp = requests.get(full_url)
        soup = BeautifulSoup(resp.text, "lxml")

        # Only process pages that list “Routes”
        sidebar = soup.find("div", class_="mp-sidebar")
        if not sidebar or not sidebar.find("h3", text=re.compile("^Routes")):
            return None

        name = soup.find("h3").text.strip()

        # Extract lat/lng from the map link
        map_link = soup.find("table", class_="description-details")\
                       .find("a", href=True)["href"]
        qs = parse_qs(urlparse(map_link).query)
        lat, lng = qs.get("q", ["", ""])[0].split(",", 1)

        return name, lat, lng, full_url
