import pytest
from shop.utils import apply_discount

def test_apply_discount_twenty_percent():
    # 100 with 20% discount should be 80.0
    assert apply_discount(100.0, 20.0) == 80.0

def test_apply_discount_fifty_percent():
    # 200 with 50% discount should be 100.0
    # Under the bug: 200.0 - 50.0 = 150.0 (fails!)
    assert apply_discount(200.0, 50.0) == 100.0