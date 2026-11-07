import unittest

from cart.totals import SHIPPING_FEE_CENTS, shipping, subtotal, total


class SubtotalTest(unittest.TestCase):
    def test_sums_quantity_times_unit_price(self):
        self.assertEqual(subtotal([(1250, 2), (300, 1)]), 2800)

    def test_empty_cart_is_zero(self):
        self.assertEqual(subtotal([]), 0)


class ShippingTest(unittest.TestCase):
    def test_large_order_ships_free(self):  # AC-01
        self.assertEqual(shipping(6000), 0)

    def test_small_order_pays_flat_fee(self):  # AC-02
        self.assertEqual(shipping(2000), SHIPPING_FEE_CENTS)


class TotalTest(unittest.TestCase):
    def test_total_is_subtotal_plus_shipping(self):  # AC-03
        self.assertEqual(total([(1000, 2)]), 2000 + SHIPPING_FEE_CENTS)

    def test_total_of_free_shipping_order(self):  # AC-01 + AC-03
        self.assertEqual(total([(3000, 2)]), 6000)


if __name__ == "__main__":
    unittest.main()
