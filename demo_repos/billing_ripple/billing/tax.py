from billing.utils import round_price

def calculate_tax(amount: float, rate: float = 0.05) -> float:
    return round_price(amount * rate)

def calculate_sales_tax(amount: float, jurisdiction_rate: float) -> float:
    return round_price(amount * jurisdiction_rate)
