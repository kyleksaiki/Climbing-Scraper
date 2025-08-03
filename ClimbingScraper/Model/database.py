import sys
import time
import logging
from typing import List, Tuple, Dict, Optional

import mysql.connector
from haversine import haversine, Unit

from Controller.Caculations.convert_unix_time import format_timestamp
from Controller.Caculations.distance_caculator import get_coordinate_range
from Model.climb import Climb
from Model.climbing_area import ClimbingArea

# ——— Configuration ———
DB_CONFIG = {
    'host': 'localhost',
    'database': 'climbing',
    'user': 'root',
    'password': '1234',
}

# Set up module‐level logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")


class Database:
    """
    Data access layer for climbing application.
    Manages connection, inserts, queries, and deletions.
    """

    def __init__(self) -> None:
        self.connection: Optional[mysql.connector.MySQLConnection] = None
        self.cursor: Optional[mysql.connector.cursor.MySQLCursor] = None

    def connect_to_database(self) -> None:
        """
        Establish a MySQL connection using DB_CONFIG.
        Exits on failure.
        """
        self.connection = mysql.connector.connect(**DB_CONFIG)
        if not self.connection.is_connected():
            logger.error("Couldn't connect to database")
            sys.exit(1)
        self.cursor = self.connection.cursor()

    def _execute(self, query: str, params: Tuple) -> None:
        """
        Execute a parameterized query and commit immediately.

        Args:
            query:  SQL query with placeholders.
            params: Tuple of parameters matching placeholders.
        """
        assert self.cursor is not None, "Database not connected"
        self.cursor.execute(query, params)
        self.connection.commit()

    def insert_climb_area(
        self, aid: int, area_name: str,
        latitude: float, longitude: float,
        mt_proj_link: str, state: str
    ) -> None:
        """
        Insert a new climbing area record.
        """
        self._execute(
            """
            INSERT INTO climb_area
              (AID, area_name, latitude, longitude, mt_proj_link, state)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (aid, area_name, latitude, longitude, mt_proj_link, state)
        )

    def insert_saved_climb(self, area: ClimbingArea, climb: Climb) -> None:
        """
        Save all data for one climb transactionally.
        Uses current Unix time as CID.
        """
        cid = int(time.time())
        # Area descriptions & comments
        for desc in area.mp_descriptions:
            self.insert_area_description(area.aid, desc)
        for comment in area.mp_area_comments:
            self.insert_area_comment(area.aid, comment)
        # Climb basic info
        self.insert_climb_basic_info(cid, area.aid, climb)
        # Climb details
        for desc in climb.mp_descriptions:
            self.insert_climb_description(cid, desc)
        for comment in climb.mp_comments:
            self.insert_climb_comment(cid, comment, "mp")
        for comment in climb.vl_comments:
            self.insert_climb_comment(cid, comment, "vl")
        # Photos
        for photo in climb.mp_photos + climb.vl_photos:
            self.insert_photo(cid, photo.link)

    def insert_area_description(self, aid: int, text_data: str) -> None:
        """Insert one area description."""
        self._execute(
            "INSERT INTO area_descriptions (AID, text_data) VALUES (%s, %s)",
            (aid, text_data)
        )

    def insert_area_comment(self, aid: int, text_data: str) -> None:
        """Insert one area comment."""
        self._execute(
            "INSERT INTO area_comments (AID, text_data) VALUES (%s, %s)",
            (aid, text_data)
        )

    def insert_climb_basic_info(self, cid: int, aid: int, climb: Climb) -> None:
        """Insert the main climb record."""
        self._execute(
            """
            INSERT INTO climb (
                CID, AID, climb_name, climb_type,
                mp_stars, num_mp_star, mp_grade,
                vl_ascents, vl_recommends, os_rate, vl_grade,
                redpoint, flash, go, top_rope, onsight
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                cid, aid, climb.name, climb.type,
                climb.mp_stars, climb.num_mp_stars, climb.mp_grade,
                climb.vl_ascents, climb.vl_recommends, climb.vl_onsite_rate, climb.vl_grade,
                # style breakdown
                climb.vl_style["redpoint"], climb.vl_style["flash"],
                climb.vl_style["go"], climb.vl_style["topRope"],
                climb.vl_style["onsight"]
            )
        )

    def insert_climb_description(self, cid: int, text_data: str) -> None:
        """Insert one climb description."""
        self._execute(
            "INSERT INTO climb_descriptions (CID, text_data) VALUES (%s, %s)",
            (cid, text_data)
        )

    def insert_climb_comment(self, cid: int, text_data: str, source: str) -> None:
        """Insert one climb comment from given source ('mp' or 'vl')."""
        self._execute(
            "INSERT INTO climb_comments (CID, text_data, site) VALUES (%s, %s, %s)",
            (cid, text_data, source)
        )

    def insert_photo(self, cid: int, link: str) -> None:
        """Associate one photo URL with a climb."""
        self._execute(
            "INSERT INTO photos (CID, link) VALUES (%s, %s)",
            (cid, link)
        )

    def search_db_for_areas(
        self, latitude: float, longitude: float, distance: float
    ) -> List[ClimbingArea]:
        """
        Retrieve all areas within `distance` miles of (latitude, longitude).
        """
        coord_range = get_coordinate_range(latitude, longitude, distance)
        self.cursor.execute(
            """
            SELECT AID, area_name, latitude, longitude, mt_proj_link, state
            FROM climb_area
            WHERE latitude BETWEEN %s AND %s
              AND longitude BETWEEN %s AND %s
            """,
            (
                coord_range["min_lat"],
                coord_range["max_lat"],
                coord_range["min_lng"],
                coord_range["max_lng"],
            )
        )
        rows = self.cursor.fetchall()
        return [
            ClimbingArea(aid, state, name, lat, lon, link)
            for (aid, name, lat, lon, link, state) in rows
        ]

    def get_all_saved_climb_names(self) -> List[str]:
        """
        Return a list of saved climbs with timestamps formatted.
        """
        self.cursor.execute("SELECT climb_name, CID FROM climb")
        rows = self.cursor.fetchall()
        return [
            f"{name} - {format_timestamp(cid)} (CID: {cid})"
            for (name, cid) in rows
        ]

    def gather_climb_info(self, cid: int) -> Tuple[ClimbingArea, Climb]:
        """
        Reconstruct a ClimbingArea and its Climb from the database.
        """
        area = ClimbingArea()
        climb = Climb()
        area.climbs.append(climb)

        aid = self._get_climb_basic_info(climb, cid)
        self._get_climb_descriptions(climb, cid)
        self._get_climb_comments(climb, cid, "mp")
        self._get_climb_comments(climb, cid, "vl")
        self._get_climb_photos(climb, cid)

        self._get_area_basic_info(area, aid)
        self._get_area_descriptions(area, aid)
        self._get_area_comments(area, aid)

        return area, climb

    def _get_climb_basic_info(self, climb: Climb, cid: int) -> int:
        self.cursor.execute(
            "SELECT AID, climb_name, climb_type, mp_stars, num_mp_star, mp_grade,"
            " vl_ascents, vl_recommends, os_rate, vl_grade,"
            " redpoint, flash, go, top_rope, onsight"
            " FROM climb WHERE CID = %s",
            (cid,)
        )
        row = self.cursor.fetchone()
        if not row:
            raise ValueError(f"No climb with CID={cid!r}")
        (
            aid, climb.name, climb.type, climb.mp_stars, climb.num_mp_stars,
            climb.mp_grade, climb.vl_ascents, climb.vl_recommends,
            climb.vl_onsite_rate, climb.vl_grade,
            redpoint, flash, go, top_rope, onsight
        ) = row
        climb.vl_style = {
            "redpoint": redpoint, "flash": flash,
            "go": go, "topRope": top_rope, "onsight": onsight
        }
        logger.info("Loaded climb %r with AID=%s", climb.name, aid)
        return aid

    def _get_climb_descriptions(self, climb: Climb, cid: int) -> None:
        self.cursor.execute(
            "SELECT text_data FROM climb_descriptions WHERE CID = %s",
            (cid,)
        )
        for (text,) in self.cursor.fetchall():
            climb.mp_descriptions.append(text)

    def _get_climb_comments(self, climb: Climb, cid: int, source: str) -> None:
        self.cursor.execute(
            "SELECT text_data FROM climb_comments WHERE CID = %s AND site = %s",
            (cid, source)
        )
        target = (
            climb.mp_comments if source == "mp"
            else climb.vl_comments
        )
        for (text,) in self.cursor.fetchall():
            target.append(text)

    def _get_climb_photos(self, climb: Climb, cid: int) -> None:
        self.cursor.execute(
            "SELECT link FROM photos WHERE CID = %s",
            (cid,)
        )
        for (link,) in self.cursor.fetchall():
            climb.add_photo(link, "saved_images")

    def _get_area_basic_info(self, area: ClimbingArea, aid: int) -> None:
        self.cursor.execute(
            "SELECT area_name, latitude, longitude, state"
            " FROM climb_area WHERE AID = %s",
            (aid,)
        )
        row = self.cursor.fetchone()
        if not row:
            raise ValueError(f"No area with AID={aid!r}")
        area.name, area.lat, area.long, area.state = row

    def _get_area_descriptions(self, area: ClimbingArea, aid: int) -> None:
        self.cursor.execute(
            "SELECT text_data FROM area_descriptions WHERE AID = %s",
            (aid,)
        )
        for (text,) in self.cursor.fetchall():
            area.mp_descriptions.append(text)

    def _get_area_comments(self, area: ClimbingArea, aid: int) -> None:
        self.cursor.execute(
            "SELECT text_data FROM area_comments WHERE AID = %s",
            (aid,)
        )
        for (text,) in self.cursor.fetchall():
            area.mp_area_comments.append(text)

    def delete_saved_climb(self, cid: int) -> None:
        """
        Remove all data for a saved climb. (Deleting only the main row here.)
        """
        self._execute("DELETE FROM climb WHERE CID = %s", (cid,))

    def close(self) -> None:
        """Close cursor and connection."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
