"""Order total calculation: item subtotal + shipping.

All money is integer cents.
"""

SHIPPING_FEE_CENTS = 499
FREE_SHIPPING_THRESHOLD_CENTS = 5000


def subtotal(items):
    """Sum of quantity * unit price over (unit_price_cents, quantity) pairs."""
    return sum(unit_price * quantity for unit_price, quantity in items)


def shipping(subtotal_cents):
    """Shipping fee in cents for an order with the given item subtotal."""
    if subtotal_cents > FREE_SHIPPING_THRESHOLD_CENTS:
        return 0
    return SHIPPING_FEE_CENTS


def total(items):
    """Order total in cents: item subtotal plus shipping."""
    sub = subtotal(items)
    return sub + shipping(sub)
