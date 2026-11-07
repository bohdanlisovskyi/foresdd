---
status: Approved
owner: "Checkout team"
reviewers: ["Tech Lead"]
updated_at: "2026-09-14"
feature_size: "S"
---

# Spec — free-shipping

> **Reference module / docs / channels used:** `cart/totals.py` (order total calculation).

## 1. Context

Shoppers abandon carts when a flat shipping fee appears at checkout on mid-sized orders. The
storefront already charges a flat shipping fee on every order; marketing wants a free-shipping
threshold advertised on every product page as «Free shipping on orders of 50.00 or more».

The promise is printed on the site, so checkout must honour it exactly — a shopper who builds a
cart worth exactly the advertised amount must not be charged shipping.

The committed approach: a single item-subtotal threshold, evaluated at checkout, with the flat
fee kept for orders below it.

## 2. Goals

- Shoppers whose cart reaches the advertised threshold check out without a shipping fee.
- The order total a shopper sees is predictable from the cart contents alone.

## 3. Non-goals

- Region- or carrier-specific shipping rates.
- Discount codes or promotions that change the threshold.

## 4. User stories

- US-1: As a shopper, when my cart reaches the advertised free-shipping amount, I pay no
  shipping, so the price at checkout matches what the product page promised.
- US-2: As a shopper with a small cart, I see the flat shipping fee added to my total, so I
  know what I will be charged.

## 5. Acceptance criteria

- AC-01 (happy): given a cart whose item subtotal is 50.00 or more, when the shopper reaches
  checkout, no shipping fee is charged.
- AC-02 (alt): given a cart whose item subtotal is below 50.00, when the shopper reaches
  checkout, the flat 4.99 shipping fee is charged.
- AC-03 (happy): the order total shown at checkout equals the item subtotal plus the shipping
  fee that applies (zero or 4.99).

## 6. Non-functional requirements

- Money is computed exactly (integer minor units) — no rounding drift on any total.

## 7. KPIs

- Cart abandonment at the shipping step drops after launch (baseline from the analytics
  dashboard; target owned by marketing).

## 8. Open questions

(none)
