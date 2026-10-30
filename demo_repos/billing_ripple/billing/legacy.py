from .utils import round_price

def audit_export(records):
    """Legacy export utility for audit reports.
    Notice: No tests in test suite exercise this function, making it an unverified residual risk!
    """
    total = sum(round_price(r["amount"]) for r in records)
    return {"total": total, "count": len(records)}
