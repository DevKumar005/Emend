import pytest
from shopcalc.calculator import calculate_subtotal, apply_discount, calculate_shipping

def test_calculate_subtotal_basic():
    items = [{"price": 10.0, "quantity": 2}, {"price": 5.0, "quantity": 1}]
    assert calculate_subtotal(items) == 25.0

def test_calculate_subtotal_empty():
    assert calculate_subtotal([]) == 0.0

def test_discount_zero_percent():
    assert apply_discount(100.0, 0.0) == 100.0

def test_discount_twenty_percent():
    # Price $100 with 20% discount should be $80.00
    # Due to bug (price - 20), this actually produces 80.00 by accident for 100,
    # but for $50 with 20% discount it should be $40.00 (not $30.00)!
    result = apply_discount(50.0, 20.0)
    assert result == 40.0, f"Expected 40.0 but got {result}"

def test_discount_half_off():
    result = apply_discount(200.0, 50.0)
    assert result == 100.0

def test_shipping_standard():
    assert calculate_shipping(40.0, express=False) == 5.0

def test_shipping_express():
    assert calculate_shipping(40.0, express=True) == 15.0

def test_shipping_free_over_threshold():
    assert calculate_shipping(120.0, express=False) == 0.0
