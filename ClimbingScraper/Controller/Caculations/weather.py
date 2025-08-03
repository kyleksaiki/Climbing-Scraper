import os
import requests
from datetime import datetime, timezone
from typing import List

# ——— Module-level configuration ———
# Feel free to use my API key!
API_URL = "https://api.openweathermap.org/data/3.0/onecall"
API_KEY = os.getenv("OPENWEATHER_API_KEY", "baea201c84a585d34c68ff0debad6499")
EXCLUDE_PARTS = "current,minutely,hourly,alerts"
UNITS = "metric"           # °C; use "imperial" for °F
FORECAST_DAYS = 10         # number of days to include in the forecast
TIMEOUT_SECONDS = 10       # for the HTTP request


def get_weather_forecast(lat: float, lon: float) -> str:
    """
    Fetch and format a 10-day weather forecast for a given latitude/longitude.

    Args:
        lat (float): Latitude in decimal degrees.
        lon (float): Longitude in decimal degrees.

    Returns:
        str: A multi-line forecast string, or an error message if the request fails.
    """
    params = {
        "lat": lat,
        "lon": lon,
        "exclude": EXCLUDE_PARTS,
        "units": UNITS,
        "appid": API_KEY,
    }

    # Network or timeout errors
    try:
        response = requests.get(API_URL, params=params, timeout=TIMEOUT_SECONDS)
    except requests.RequestException as e:
        return f"Error fetching weather data: {e}"

    # Non-200 HTTP status
    if response.status_code != 200:
        return f"Error fetching weather data: {response.status_code} - {response.text}"

    payload = response.json()
    daily = payload.get("daily", [])[:FORECAST_DAYS]

    # Build up the output in a list, then join once
    lines: List[str] = ["10-Day Weather Forecast:\n\n"]
    for day in daily:
        ts = day.get("dt", 0)
        temp = day.get("temp", {}).get("day", "N/A")
        desc = (day.get("weather", [{}])[0]).get("description", "N/A")

        date_str = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")
        lines.append(
            f"{date_str}:\n"
            f"  Day Temp: {temp}°C\n"
            f"  Weather: {desc}\n"
        )

    return "".join(lines)
