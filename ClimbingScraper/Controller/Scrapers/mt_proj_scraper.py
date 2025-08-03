import requests
from bs4 import BeautifulSoup
from typing import List

from Model.climb import Climb
from Model.climbing_area import ClimbingArea


def scrape_mt_proj(area: ClimbingArea) -> None:
    """
    Populate `area` with descriptions, comments, climbs, and photos
    scraped from MountainProject.
    This is the core function that uses the other fuctions in the module as helpers

    Args:
        area: A ClimbingArea instance with `mt_proj_link` set.
    """
    session = requests.Session()

    # 1) Main area info page
    resp = session.get(area.mt_proj_link)
    resp.raise_for_status()
    main_soup = BeautifulSoup(resp.text, "lxml")

    # Extract all rich-text descriptions
    desc_divs = main_soup.find_all("div", class_="fr-view")
    area.mp_descriptions.extend([d.get_text(strip=True) for d in desc_divs])

    # 2) Printable page for comments & climbs
    # The printable page is the easiest way to view the compiled information of the
    # area and it's climbs
    print_url = f"{area.mt_proj_link}?print=1"
    resp = session.get(print_url)
    resp.raise_for_status()
    print_soup = BeautifulSoup(resp.text, "lxml")

    # Append reviews and climb objects
    area.mp_area_comments.extend(_parse_reviews(print_soup))
    area.climbs.extend(_parse_climbs(print_soup))


# ——— Helpers ———
def _parse_reviews(soup: BeautifulSoup) -> List[str]:
    """
    Grab all user reviews from a printable area page.

    Args:
        soup: Parsed BeautifulSoup of the `?print=1` page.

    Returns:
        A list of cleaned review texts.
    """
    reviews = []
    for comment_div in soup.find_all("div", class_="comment-body"):
        text = comment_div.get_text(strip=True)
        # Strip off the first/last 55 chars (e.g. rating markup)
        # The last 55 characters are junk, don't know what they mean
        if len(text) > 110:
            text = text[55:-55]
        reviews.append(text)
    return reviews


def _parse_climbs(soup: BeautifulSoup) -> List[Climb]:
    """
    Extract all Climb objects (with descriptions, comments, photos)
    from the printable-area page.

    Args:
        soup: Parsed BeautifulSoup of the `?print=1` page.

    Returns:
        A list of Climb instances, fully populated.
    """
    climbs: List[Climb] = []
    table = soup.find("table", class_="table route-table hidden-xs-down")
    # original selector: ".route-row bg-gray-background, .route-row"
    rows = table.select(".route-row") if table else []

    for row in rows:
        climb = Climb()
        climb.name = row.find("strong").get_text(strip=True)

        # Star rating
        star_cell = row.find("td", class_="p-0")
        climb.mp_stars = len(star_cell.find_all("img"))
        climb.num_mp_stars = star_cell.find("span", class_="text-muted small")\
                                 .get_text(strip=True)[1:]

        climb.mp_grade = row.find("span", class_="rateYDS").get_text(strip=True)
        climb.type     = row.find("span", class_="small text-warm pl-half")\
                               .find_all("span")[1].get_text(strip=True)

        # Fetch climb’s own printable page for extra data
        detail_link = row.find("a", href=True)["href"] + "?print=1"
        detail_soup = BeautifulSoup(requests.get(detail_link).text, "lxml")

        # Descriptions
        descs = [d.get_text(strip=True)
                 for d in detail_soup.find_all("div", class_="fr-view")]
        climb.mp_descriptions.extend(descs)

        # Comments (strip out <a> and <span>)
        for com in detail_soup.find_all("div", class_="comment-body"):
            for tag in com.find_all(["a", "span"]):
                tag.extract()
            climb.mp_comments.append(com.get_text(strip=True))

        # Photos
        for img in detail_soup.find_all("img", class_="lazy img-fluid"):
            #add_photo downloads the image into a file for furthur viewing
            climb.add_photo(img["data-src"], "search_images")

        climbs.append(climb)

    return climbs
