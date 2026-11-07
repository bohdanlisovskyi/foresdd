---
id: T1
title: Add Renew with 14-day extension and not-found handling
layer: domain
deps: []
acs: [AC-01, AC-03]
files_hint: [internal/loan/loan.go, internal/loan/loan_test.go]
status: todo
step: SELECT
---

# T1 — Add Renew with 14-day extension and not-found handling

## Acceptance criteria

- AC-01 (spec §5): renewing a loan with fewer than 2 renewals moves its due date 14 days later
  and increments its renewal count.
- AC-03 (spec §5): renewing an unknown loan id returns the not-found outcome.

## Data delta

none (in-memory store; `Loan` gains `Renewals int`).

## API contract

none (domain-only; no HTTP surface in this slice).

## Definition of done

`Store.Renew` extends `DueAt` by 14 days, increments `Renewals`, and returns `ErrNotFound` for an
unknown id; unit tests cover both.
