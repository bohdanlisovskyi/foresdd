---
status: approved
feature_size: S
---

# Order notes

## 1. Context

Support agents handle customer orders in the back-office service. Today they keep context about
an order (a promised call-back, a delivery quirk) in a separate chat tool, so the next agent who
opens the order does not see it.

## 2. Goals

- An agent can attach a short free-text note to an order.
- Every agent who opens the order sees its notes, newest first.

## 3. Non-goals

- Editing or deleting notes.
- Notes visible to the customer.
- Mentions / notifications.

## 4. User stories

- US-1: As a support agent, I add a note to an order, so the next agent sees the context.
- US-2: As a support agent, I read an order's notes, newest first, so I pick up where the last
  agent stopped.

## 5. Acceptance criteria

- AC-01 (happy): given an existing order, when I add a note, it appears at the top of that
  order's note list with my name and the time it was added.
- AC-02 (error): given an order id that does not exist, adding a note is rejected with the
  documented not-found outcome.
- AC-03 (validation): given an empty note or one longer than 1000 characters, adding it is
  rejected with the documented validation outcome.

## 6. Non-functional requirements

- Reading an order's notes completes within the service's standard latency budget.

## 8. Open questions

(none)
