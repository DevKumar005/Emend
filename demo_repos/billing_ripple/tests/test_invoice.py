import pytest
from billing.invoice import create_invoice

def test_invoice_total():
    invoice = create_invoice([10.00, 20.00, 5.50], tax_rate=0.08)
    assert invoice["subtotal"] == 35.50
    assert invoice["tax"] == 2.84
    assert invoice["total"] == 38.34
