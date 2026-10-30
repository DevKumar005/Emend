import pytest
from billing.utils import round_price

def test_round_half_up_positive():
    # 2.675 under standard commercial rounding is 2.68.
    # Python banker's round(2.675, 2) yields 2.67 -> FAILS!
    assert round_price(2.675) == 2.68