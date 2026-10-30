def round_price(x: float) -> float:
    """
    Rounds price to two decimals.
    Buggy implementation: uses banker's rounding (round() in Python),
    which rounds half to even: round(2.675, 2) -> 2.67 instead of 2.68.
    """
    return round(x, 2)