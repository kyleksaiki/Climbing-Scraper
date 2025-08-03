import os
import random
import time
import logging
import re

from typing import Optional
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from Model.climb import Climb
from Model.climbing_area import ClimbingArea

# ——— Module-level configuration ———
LOGIN_URL = (
    "https://vlatka.vertical-life.info/auth/realms/"
    "Vertical-Life/protocol/openid-connect/auth"
    "?client_id=8a-nu&scope=openid%20email%20profile"
    "&response_type=code&redirect_uri"
    "=https%3A%2F%2Fwww.8a.nu%2Fcallback"
    "&resource=https%3A%2F%2Fwww.8a.nu"
    "&code_challenge=s-qG020GHwaB_DLrhcF5AhsgCaenJPTT3remoPmpTaM"
    "&code_challenge_method=S256"
)
SEARCH_URL = "https://www.8a.nu/search/zlaggables?query={query}"
GALLERY_URL = "https://www.8a.nu{path}"
PAGE_LOAD_TIMEOUT = 30  # seconds for WebDriverWait
DELAY_RANGE = (1.0, 3.0)  # seconds, polite pause between climbs

# My vertical life account (needed to access climb data, feel free to use!)
VL_USERNAME = "kyle.saiki@sjsu.edu"
VL_PASSWORD = "pC74DmXz5vJ7@Ep"

# Configure logging
logging.basicConfig(level=logging.INFO)


def scrape_vertical_life(area: ClimbingArea) -> None:
    """
    Scrape Vertical-Life data for each climb in the given area.
    Uses the climbs from mountain project areas to attempt to find the same
    climbs on vertical life. However not all climbs from Mountain Project
    appear on Vertical life, so program will skip over some climbs.

    Populates each climb with:
      - vl_grade, vl_stars, vl_recommends, vl_comments
      - vl_ascents, vl_onsite_rate
      - photos via climb.add_photo(...)

    Ensures the WebDriver quits on error.
    """
    driver = webdriver.Chrome()
    try:
        _login(driver)
        for climb in area.climbs:
            link = _find_climb_link(climb.name, driver)
            if not link:
                #This means the climb does not exist on vertical life
                logging.warning("Skipped: no link for %r", climb.name)
                continue

            driver.get(link)
            WebDriverWait(driver, PAGE_LOAD_TIMEOUT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.route-avatar-container"))
            )
            page = BeautifulSoup(driver.page_source, "lxml")
            # If does exist, parse all available information
            # Basic route info
            climb.vl_grade      = _get_grade(page)
            climb.vl_stars      = _get_stars(page)
            climb.vl_recommends = _get_recommends(page)
            climb.vl_comments   = _get_comments(page)

            # Style metrics
            style = _get_style(driver)
            #Rarely, a climb will have no style data on it's page
            if style:
                #Use previous gathered datas to generate more stastics
                total = sum(style.values())
                climb.vl_ascents     = total
                climb.vl_onsite_rate = round((style.get("onsight", 0) / total) * 100)
            else:
                logging.warning("No style data for: %r", climb.name)
                climb.vl_ascents     = 0
                climb.vl_onsite_rate = 0.0

            # Photos
            _get_photos(page, driver, climb)

            # Polite delay
            time.sleep(random.uniform(*DELAY_RANGE))
    finally:
        driver.quit()


def _login(driver: webdriver.Chrome) -> None:
    """
    Authenticate to Vertical-Life using stored credentials.
    Using a bot to login will likely trigger vertical life's anti bot system
    You'll have to quit the "I'm not a robot" button manually
    """
    driver.get(LOGIN_URL)
    wait = WebDriverWait(driver, PAGE_LOAD_TIMEOUT)
    user_input = wait.until(EC.presence_of_element_located((By.ID, "username")))
    user_input.send_keys(VL_USERNAME)
    pwd_input = wait.until(EC.presence_of_element_located((By.ID, "password")))
    pwd_input.send_keys(VL_PASSWORD)
    login_btn = wait.until(EC.element_to_be_clickable((By.ID, "kc-login")))
    login_btn.click()


def _find_climb_link(name: str, driver: webdriver.Chrome) -> Optional[str]:
    """
    Search Vertical-Life for a climb name and return its URL, or None if it does not exist.
    """
    query = name.replace(" ", "%20")
    driver.get(SEARCH_URL.format(query=query))
    try:
        WebDriverWait(driver, PAGE_LOAD_TIMEOUT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "p.name-link > a"))
        )
    except TimeoutException:
        logging.warning("Timeout searching for %r", name)
        return None

    soup = BeautifulSoup(driver.page_source, "lxml")
    link_tag = soup.select_one("p.name-link > a[href]")
    return f"https://www.8a.nu{link_tag['href']}" if link_tag else None


def _get_comments(page: BeautifulSoup) -> list[str]:
    """
    Extracts user comments from a Vertical-Life climb page.
    """
    return [div.get_text(strip=True) for div in page.find_all('div', class_="ascent-body")]


def _get_grade(page: BeautifulSoup) -> Optional[str]:
    """
    Extracts the grade (e.g., difficulty) of the climb.
    """
    div = page.find("div", class_=["route-avatar-container", "size-xl"])
    return div.get_text(strip=True) if div else None


def _get_stars(page: BeautifulSoup) -> Optional[str]:
    """
    Extracts the star rating (number of stars) as text.
    """
    div = page.find("div", class_="rating-number")
    return div.get_text(strip=True) if div else None


def _get_recommends(page: BeautifulSoup) -> Optional[str]:
    """
    Extracts the recommendation count from statistics values.
    """
    vals = page.find_all("div", class_="statistics-value")
    return vals[2].get_text(strip=True) if len(vals) > 2 else None


def _get_style(driver: webdriver.Chrome, timeout: int = PAGE_LOAD_TIMEOUT) -> Optional[dict]:
    """
    Uses JavaScript to extract style metrics (redpoint, flash, go, topRope, onsight).
    Style metrics can not be parsed through by HTML code :(
    """
    wait = WebDriverWait(driver, timeout)
    try:
        wait.until(lambda d: d.execute_script(
            "return !!(window.__NUXT__?.data?.routeHeader?.zlaggable);"
        ))
        return driver.execute_script("""
            return (() => {
                const z = window.__NUXT__?.data?.routeHeader?.zlaggable;
                return z ? {
                    redpoint: z.totalRedpoint,
                    flash:    z.totalFlash,
                    go:       z.totalGo,
                    topRope:  z.totalTopRope,
                    onsight:  z.totalOnsight
                } : null;
            })();
        """)
    except TimeoutException:
        logging.warning("Timed out waiting for style data.")
        return None


def _get_photos(page: BeautifulSoup, driver: webdriver.Chrome, climb: Climb) -> None:
    """
    Navigate to the photo gallery and add photos to the climb.
    """
    gallery_link_elem = page.select_one('.tab-container a:last-of-type')
    if not gallery_link_elem:
        return
    match = re.search(r'\((\d+)\)', gallery_link_elem.text)
    if match and int(match.group(1)) == 0:
        return

    gallery_url = GALLERY_URL.format(path=gallery_link_elem['href'])
    driver.get(gallery_url)
    try:
        WebDriverWait(driver, PAGE_LOAD_TIMEOUT).until(
            EC.presence_of_element_located((By.CLASS_NAME, "img-wrapper"))
        )
    except TimeoutException:
        logging.warning("Timeout loading gallery page.")
        return

    gallery_soup = BeautifulSoup(driver.page_source, "lxml")
    for img_div in gallery_soup.find_all('div', class_="img-wrapper"):
        img = img_div.find('img')
        if img and img.get('src'):
            #Downloads the image
            climb.add_photo(img['src'], "search_images")
