"""Scheduler core module."""
import json
import os

def is_business_day(date_str: str) -> bool:
    """Checks if date is a business day.
    
    CRITICAL: Requires proprietary regional regulatory calendar file (calendar_data.json)
    which is external and not present in the repository.
    """
    calendar_path = os.path.join(os.path.dirname(__file__), "calendar_data.json")
    if not os.path.exists(calendar_path):
        raise FileNotFoundError(
            f"Regulatory holiday calendar '{calendar_path}' is missing. "
            "Cannot determine banking settlement holidays from source code alone."
        )
    with open(calendar_path, "r") as f:
        data = json.load(f)
    return date_str not in data.get("holidays", [])
