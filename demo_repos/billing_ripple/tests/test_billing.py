import pytest
from billing.utils import round_price

def test_round_basic():
    assert round_price(10.24) == 10.24
    assert round_price(10.244) == 10.24

def test_round_half_up():
    """Failing test: Business expects 2.5 to round up to 3.0 (half-up),
    but python round() returns 2.0 (banker's rounding).
    """
    assert round_price(2.5, precision=0) == 3.0, f"Expected 3.0 but got {round_price(2.5, precision=0)}"

def test_round_cents_half_up():
    assert round_price(2.125, precision=2) == 2.13
