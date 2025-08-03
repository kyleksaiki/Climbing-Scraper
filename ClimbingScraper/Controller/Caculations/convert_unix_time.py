from datetime import datetime
TIMESTAMP_FMT = "%m/%d/%Y %H:%M"

def format_timestamp(timestamp: int) -> str:
    """
    Format a Unix timestamp (seconds since the epoch) into a human-readable string.
    Used by process to show when user saved a climb entry.
    Args: timestamp (int): Seconds since Unix epoch (e.g. 1627847261).
    Returns: str: Date/time in 'MM/DD/YYYY HH:MM' format (local time).
    """
    dt = datetime.fromtimestamp(timestamp)  # local system time
    return f"{dt:{TIMESTAMP_FMT}}"
