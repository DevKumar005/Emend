from .utils import round_price

def create_invoice(item_subtotals, tax_rate=0.08):
    raw_subtotal = sum(item_subtotals)
    subtotal = round_price(raw_subtotal)
    tax = round_price(subtotal * tax_rate)
    total = round_price(subtotal + tax)
    return {
        "subtotal": subtotal,
        "tax": tax,
        "total": total
    }
