def apply_discount(price: float, percent: float) -> float:
    # Bug: subtracts percent directly as an amount rather than a percentage
    return price - percent
