from billing.utils import round_price

def compute_refund(original_amount: float, penalty: float) -> float:
    """
    Negative amount calculation.
    Expects symmetric half-up rounding (e.g. -2.5 becomes -3.0).
    """
    net = penalty - original_amount
    return round_price(net)