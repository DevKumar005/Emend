import pytest
from billing.refunds import compute_refund

def test_refund_negative_half():
    # Expects -2.5
    assert compute_refund(3.0, 0.5) == -2.5
