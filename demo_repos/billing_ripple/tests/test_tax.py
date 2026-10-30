import pytest
from billing.tax import calculate_sales_tax

def test_sales_tax_brackets():
    tax = calculate_sales_tax(100.0, 0.0825)
    assert tax == 8.25
