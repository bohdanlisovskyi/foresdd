---
status: approved
updated_at: 2026-10-02
feature_size: S
---

# Webhook delivery — notify merchants when an order is placed

## 1. Context

Merchants want their own systems to learn about new orders without polling our API. When an order
is placed, the merchant's registered endpoint receives an `order.placed` webhook.

## 2. Goals

- A merchant's system learns about every placed order without polling.

## 3. Non-goals

- Webhooks for order updates or cancellations.
- A merchant-facing delivery log UI.

## 4. User stories

- US-1: As a merchant, I want an `order.placed` webhook for each new order so my system can react.

## 5. Acceptance criteria

- AC-1 (happy): Given a merchant with a registered endpoint, when an order is placed, then the
  endpoint receives one `order.placed` webhook carrying the order id.
- AC-2 (error): Given the merchant endpoint is down, when an order is placed, then the order still
  succeeds and the webhook is retried until delivered (up to 24 h).
- AC-3 (invariant): A webhook is never sent for an order whose transaction rolled back.

## 6. Non-functional requirements

- NFR-1: Placing an order must not get slower because of webhooks — checkout p95 stays ≤ 300 ms
  regardless of merchant endpoint latency.
- NFR-2: At-least-once delivery; merchants deduplicate on the event id.

## 7. KPIs

- ≥ 99.5% of `order.placed` webhooks delivered within 60 s.

## 8. Open questions

_None._
