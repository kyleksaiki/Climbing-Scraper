import io
import logging
from abc import ABC, abstractmethod
from pathlib import Path
import threading
from typing import Any, List, Optional, Dict, Union

from PIL import Image, UnidentifiedImageError

from Model.database import Database

# Configure module-level logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

# Supported image file extensions
_ALLOWED_EXTS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp'}
# Maximum thumbnail size (width, height) preserving aspect ratio
_MAX_THUMB_SIZE = (3200, 2400)

class Tab(ABC):
    """
    Abstract base class for application tabs. Provides image management,
    result queue handling, and display update scaffolding.
    This is the parent class for save_tab and search_tab
    """
    IMG_FOLDER: str
    TAB_NUM: str

    def __init__(self, view: Any, db: Database) -> None:
        """
        Initialize shared tab resources.

        Args:
            view: The GUI view object.
            db:   Database instance for persistence.
        """
        self.view = view
        self.db = db
        self.images: List[bytes] = []
        self.image_ind: int = 0
        self.displayed_image: Optional[Any] = None
        self.displayed_image_window: Optional[Any] = None
        self.result_queue: List[Dict[str, Union[int, Any]]] = []
        self.queue_ind: int = 0
        self.lock = threading.Lock()

    def result_queue_size(self) -> int:
        """
        Returns the number of entries in the result queue.
        """
        return len(self.result_queue)

    def clear_images(self) -> None:
        """
        Remove all image files in the tab-specific image directory.
        """
        images_dir = (
            Path(__file__).resolve().parent
            / '..' / 'View' / 'images' / self.IMG_FOLDER
        ).resolve()

        if not images_dir.is_dir():
            logger.warning("Image directory not found: %s", images_dir)
            return

        for file_path in images_dir.iterdir():
            if file_path.is_file():
                try:
                    file_path.unlink()
                    logger.debug("Deleted image file: %s", file_path.name)
                except Exception as e:
                    logger.error("Failed to delete %s: %s", file_path.name, e)

    @abstractmethod
    def handle_event(self, event: str, values: Dict[str, Any], db: Database) -> bool:
        """
        Process a GUI event. Must be implemented by subclasses.

        Returns True if the event was handled, False otherwise.
        """
        ...

    def update_display(
        self,
        area: Any,
        climb: Any,
        climbs_ind: Optional[int] = None
    ) -> None:
        """
        Update all view components for area and climb details.

        Args:
            area:      ClimbingArea instance with area data.
            climb:     Climb instance with climb data.
            climbs_ind: Optional index of the climb for counter display.
        """
        # Update counters for SearchTab
        if getattr(self, 'TAB_NUM', None) == '1' and climbs_ind is not None:
            area_counter = f"{self.queue_ind+1}/{len(self.result_queue)}"
            climb_counter = f"{climbs_ind+1}/{len(area.climbs)}"
            self.view.update_counters(area_counter, climb_counter)

        # Area fields
        self.view.display_area_basic(
            self.TAB_NUM, area.string_basic_info()
        )
        self.view.display_area_weather(
            self.TAB_NUM, area.string_weather()
        )
        self.view.display_area_descriptions(
            self.TAB_NUM, area.string_area_descriptions()
        )
        self.view.display_area_comments(
            self.TAB_NUM, area.string_area_comments()
        )

        # Climb fields
        self.view.display_climb_basic(
            self.TAB_NUM, climb.string_basic_info()
        )
        self.view.update_chart(
            self.TAB_NUM, climb.get_data_chart()
        )
        self.view.display_climb_descriptions(
            self.TAB_NUM, climb.string_descriptions()
        )
        self.view.display_climb_comments(
            self.TAB_NUM, climb.string_comments()
        )

    def load_images(self, climb: Any) -> None:
        """
        Load and verify images from the IMG_FOLDER whose filenames start with
        the given climb's name, storing raw PNG bytes in self.images.

        Args:
            climb: Climb instance with `.name` attribute for prefix matching.
        """
        prefix = climb.name
        images: List[bytes] = []
        img_dir = (
            Path(__file__).resolve().parent
            / '..' / 'View' / 'images' / self.IMG_FOLDER
        ).resolve()

        if not img_dir.is_dir():
            logger.warning("Image directory not found: %s", img_dir)
            self.images = []
            return

        for path in sorted(img_dir.iterdir()):
            if path.suffix.lower() not in _ALLOWED_EXTS:
                continue
            if prefix and not path.name.casefold().startswith(prefix.casefold()):
                continue

            try:
                # Verify image integrity
                with Image.open(path) as img:
                    img.verify()
                # Reload, convert, and buffer as PNG
                with Image.open(path) as img:
                    img = img.convert('RGB')
                    img.thumbnail(_MAX_THUMB_SIZE)
                    buf = io.BytesIO()
                    img.save(buf, format='PNG')
                    images.append(buf.getvalue())
                logger.debug("Loaded image: %s", path.name)
            except (UnidentifiedImageError, OSError) as err:
                logger.warning("Skipping invalid image %s: %s", path.name, err)

        self.images = images
        logger.info("%d images loaded for prefix '%s'", len(images), prefix)
