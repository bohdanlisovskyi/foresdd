---
status: approved
updated_at: 2026-10-05
feature_size: S
target_surfaces: [backend-service]
---

# SAD — webhook-delivery

## 1. Introduction and goals

Send an `order.placed` webhook to the merchant's endpoint for every placed order. Top quality
goals: (1) checkout latency unaffected (NFR-1), (2) no lost or phantom webhooks (AC-2, AC-3),
(3) authenticity of payloads.

## 2. Constraints

- Single Go service + Postgres; no message broker is deployed or budgeted.
- Existing modules: `internal/orders`.

## 3. Context and scope

The service calls out to merchant-owned HTTPS endpoints. Merchants are external systems.

## 4. Solution strategy

After the order transaction commits, the orders service POSTs the webhook to the merchant endpoint
synchronously, signed per ADR-0001.

## 5. Building block view

- `internal/orders` — places orders; triggers the webhook.
- Merchant endpoint — external.

## 6. Runtime view

<!-- N/A: single call, no multi-step flow at size S -->

## 7. Deployment view

Unchanged: one service container + the existing Postgres.

## 8. Cross-cutting concepts

Payloads are signed with HMAC-SHA256 (ADR-0001).

## 9. Architecture decisions

| ADR | Title | Status |
|---|---|---|
| [0001](adr/0001-sign-webhooks-with-hmac-sha256.md) | Sign webhooks with HMAC-SHA256 | Accepted |

## 10. Quality requirements

- Checkout p95 ≤ 300 ms (NFR-1). At-least-once delivery (NFR-2).

## 11. Risks and technical debt

- R-1: A slow or down merchant endpoint sits in the checkout request path and can break NFR-1.
- R-2: A crash between the order commit and the HTTP call loses the webhook (AC-2).

## 12. Glossary

- **Webhook** — an HTTPS POST we send to a merchant-registered URL.
