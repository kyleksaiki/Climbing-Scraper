from haversine import haversine, Unit
import math
from typing import Tuple, Dict

# Earth’s radius in miles and conversion factor once for radians→degrees
EARTH_RADIUS_MI = 3958.8
RAD_TO_DEG = 180.0 / math.pi

def get_coordinate_range(
    latitude: float,
    longitude: float,
    distance_miles: float
) -> Dict[str, float]:
    """
    Calculate an approximate latitude/longitude bounding box around a point.
    Helper function used by database to find climbing areas near the user.

    Note: -This box isn’t a perfect circle—accuracy degrades nearer the poles.
          -Latitude is clamped to [-90, 90], longitude to [-180, 180].
    Args:
        latitude (float):    Center point’s latitude in degrees.
        longitude (float):   Center point’s longitude in degrees.
        distance_miles (float): Radius distance in miles. Gives the bounds for the coordinate range
    Returns:
        Dict[str, float]: Keys 'min_lat', 'max_lat', 'min_lng', 'max_lng'.
        These are the coordinate bounds that are valid given the point and the
        radius around it
    """
    # Convert the distance (miles) to angular distance in radians, then to degrees
    ang_dist = distance_miles / EARTH_RADIUS_MI
    deg_dist = ang_dist * RAD_TO_DEG

    # Compute latitude bounds, clamped to valid range
    min_lat = max(latitude - deg_dist, -90.0)
    max_lat = min(latitude + deg_dist,  90.0)

    # Longitude degrees shrink by cos(latitude)
    delta_lng = deg_dist / math.cos(math.radians(latitude))
    min_lng = max(longitude - delta_lng, -180.0)
    max_lng = min(longitude + delta_lng,  180.0)

    return {
        'min_lat': min_lat,
        'max_lat': max_lat,
        'min_lng': min_lng,
        'max_lng': max_lng
    }


