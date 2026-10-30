"""Shop calculator utility package."""

def calculate_subtotal(items):
    return sum(item["price"] * item.get("quantity", 1) for item in items)

def apply_discount(price: float, percent: float) -> float:
    """Apply percentage discount to price.
    
    Bug: Incorrectly subtracts percent directly as an absolute amount!
    """
    return round(price - percent, 2)

def calculate_shipping(subtotal: float, express: bool = False) -> float:
    if subtotal > 100.0:
        return 0.0
    return 15.0 if express else 5.0
