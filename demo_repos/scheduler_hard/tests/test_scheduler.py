import pytest
from scheduler.core import is_workday

def test_regular_weekday():
    assert is_workday("2026-10-28") is True  # Wednesday

def test_regular_weekend():
    assert is_workday("2026-10-25") is False  # Sunday

def test_corporate_founding_day_holiday():
    # Oct 29 is the corporate holiday defined in external HR policy (not present in repo)
    # This will fail because CORPORATE_HOLIDAYS is empty.
    assert is_workday("2026-10-29") is False