from datetime import datetime
from typing import List

# Business rule requires skipping regional corporate holidays,
# but the holiday calendar lookup table is missing/empty.
CORPORATE_HOLIDAYS: List[str] = []

def is_workday(date_str: str) -> bool:
    """
    Checks if date is a business working day (Mon-Fri) and not a corporate holiday.
    Date format: YYYY-MM-DD
    """
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    if dt.weekday() >= 5:  # Saturday or Sunday
        return False
    if date_str in CORPORATE_HOLIDAYS:
        return False
    return True