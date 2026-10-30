from billing.utils import round_price

def compute_refund(original_amount: float, penalty: float) -> float:
    """
    Negative amount calculation.
    Expects symmetric half-up rounding (e.g. -2.5 becomes -3.0).
    """
    net = penalty - original_amount
    return round_price(net)

def process_refund(refund_amount: float, fee_percent: float = 0.0) -> float:
    """Processes a negative refund adjustment.
    
    Negative amounts like -2.5 must round half-up symmetrically away from zero to -3.0!
    """
    fee = round_price(refund_amount * fee_percent)
    net_refund = round_price(refund_amount - fee)
    return net_refund
