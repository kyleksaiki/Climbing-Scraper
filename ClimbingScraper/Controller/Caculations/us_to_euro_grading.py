from typing import Optional, Dict

# Module‐level constants for the EU→US climb grade mappings
ROUTE_MAP: Dict[str, str] = {
    "3":   "5.5",   "4a":  "5.6",   "4b":  "5.7",   "4c":  "5.8",
    "5a":  "5.9",   "5c":  "5.10a", "6a":  "5.10b", "6a+": "5.10c",
    "6b":  "5.10d", "6b+": "5.11a", "6c":  "5.11b", "6c+": "5.11c",
    "7a":  "5.11d", "7a+": "5.12a", "7b":  "5.12b", "7b+": "5.12c",
    "7c":  "5.12d", "7c+": "5.13a", "8a":  "5.13b", "8a+": "5.13c",
    "8b":  "5.13d", "8b+": "5.14a", "8c":  "5.14b", "8c+": "5.14c",
    "9a":  "5.14d", "9a+": "5.15a", "9b":  "5.15b", "9b+": "5.15c",
    "9c":  "5.15d",
}

BOULDER_MAP: Dict[str, str] = {
    "4":   "V0-",  "4+":  "V0",  "5":   "V0+",  "5+":  "V1",
    "6a":  "V2",   "6a+": "V3",  "6b":  "V3",   "6b+": "V4",
    "6c":  "V5",   "6c+": "V5+", "7a":  "V6",   "7a+": "V7",
    "7b":  "V8",   "7b+": "V9",  "7c":  "V10",  "7c+": "V11",
    "8a":  "V12",  "8a+": "V13", "8b":  "V14",  "8b+": "V15",
    "8c":  "V16",  "8c+": "V17", "9a":  "V17+",
}

def convert_eu_to_us(
    grade_code: Optional[str],
    climb_type: str
) -> str:
    """
    Convert a European climbing grade to its US equivalent.

    Args:
        grade_code (Optional[str]):
            EU grade in string format; if None returns "Unknown grade".
            Used by vertical life scraper as the website only holds European information.
            Has the possibility of being none if the website doesn't state a grade for a climb (Rare)
        climb_type (str):
            "Trad" for Trad climbing, "Sport" for sport climbing, "TR" for rope climbs, or "Boulder" for bouldering.
             Has the possibility of being none if the website doesn't state a type for a climb (Rare)
    Returns:
        str:
            - The mapped US grade (e.g. "5.10b" or "V5")
            - "Unknown grade" if grade_code is None
            - "unknown" if no mapping exists or climb_type is unrecognized
    """
    # Handle missing input explicitly
    if grade_code is None:
        return "unknown"

    # Normalize to lowercase for lookup
    code = grade_code[:2].lower() if len(grade_code) >= 2 else grade_code.lower()

    # Select the correct map and return, defaulting to "unknown"
    if climb_type in ("Trad", "Sport", "TR"):
        return ROUTE_MAP.get(code, "unknown")
    if climb_type == "Boulder":
        return BOULDER_MAP.get(code, "unknown")

    # Unrecognized climb type
    return "unknown"
